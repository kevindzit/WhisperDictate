import io
import os
from pathlib import Path
import re
import runpy
import shutil
import sys
import tempfile
from contextlib import contextmanager, redirect_stdout
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, Mock, patch


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = 'deepdml/faster-distil-whisper-large-v3.5'


def fake_torch(cuda=False):
    return SimpleNamespace(
        __version__='test',
        cuda=SimpleNamespace(is_available=lambda: cuda),
    )


@contextmanager
def app_environment(model_text=None, cuda=False):
    with tempfile.TemporaryDirectory() as folder:
        app_path = Path(folder) / 'dictation_app.py'
        shutil.copyfile(ROOT / 'dictation_app.py', app_path)
        if model_text is not None:
            app_path.with_name('model.txt').write_text(model_text, encoding='utf-8')

        loader = Mock()
        modules = {
            'faster_whisper': SimpleNamespace(WhisperModel=loader),
            'torch': fake_torch(cuda),
            'pyaudio': SimpleNamespace(paInt16=8, PyAudio=Mock()),
            'keyboard': MagicMock(),
            'numpy': MagicMock(),
            'pyperclip': MagicMock(),
            'pystray': MagicMock(),
            'PIL': SimpleNamespace(Image=MagicMock(), ImageDraw=MagicMock()),
        }
        output = io.StringIO()
        # stub hardware and model loading, while running the actual app settings code
        with patch.dict(sys.modules, modules), redirect_stdout(output):
            yield lambda: runpy.run_path(str(app_path)), loader, output


def setup_verification_code():
    setup = (ROOT / 'setup.ps1').read_text(encoding='utf-8-sig')
    match = re.search(
        r"\$verifyScript\s*=\s*@(?P<quote>['\"])\r?\n(?P<code>.*?)\r?\n(?P=quote)@",
        setup, re.DOTALL,
    )
    if match is None:
        raise AssertionError('Could not find the setup verification Python code')
    return match.group('code')


class ModelSelectionTests(unittest.TestCase):
    def test_missing_settings_preserves_current_default(self):
        with app_environment() as (load, model, _):
            load()
            model.assert_called_once_with(DEFAULT_MODEL, device='cpu', compute_type='float32')

    def test_each_saved_model_reaches_the_loader(self):
        choices = {
            'distil-large-v3.5': DEFAULT_MODEL,
            'turbo': 'turbo',
            'large-v3': 'large-v3',
            'small': 'small',
        }
        for choice, expected in choices.items():
            with self.subTest(model=choice):
                with app_environment(choice) as (load, model, _):
                    load()
                    model.assert_called_once_with(expected, device='cpu', compute_type='float32')

    def test_windows_utf8_bom_whitespace_and_case_are_handled(self):
        with app_environment('\ufeff TURBO\r\n') as (load, model, _):
            load()
            model.assert_called_once_with('turbo', device='cpu', compute_type='float32')

    def test_settings_are_read_beside_the_app(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'model.txt').write_text('turbo', encoding='utf-8')
            try:
                os.chdir(folder)
                with app_environment('large-v3') as (load, model, _):
                    load()
                    model.assert_called_once_with('large-v3', device='cpu', compute_type='float32')
            finally:
                os.chdir(previous)

    def test_invalid_or_empty_settings_stop_before_model_loading(self):
        for choice in ('unknown-model', '', '  \n'):
            with self.subTest(model=choice):
                with app_environment(choice) as (load, model, _):
                    with self.assertRaisesRegex(ValueError, 'model.txt'):
                        load()
                    model.assert_not_called()

    def test_gpu_settings_are_preserved(self):
        with app_environment('turbo', cuda=True) as (load, model, _):
            load()
            model.assert_called_once_with('turbo', device='cuda', compute_type='float16')

    def test_startup_message_names_the_selected_model(self):
        with app_environment('small') as (load, _, output):
            app = load()
            app['main']()
            self.assertIn('Model: small (faster-whisper)', output.getvalue())

    def test_setup_verification_uses_the_actual_backend(self):
        loader = Mock()
        modules = {
            'torch': fake_torch(),
            'faster_whisper': SimpleNamespace(WhisperModel=loader),
            'whisper': None,
        }
        with patch.dict(sys.modules, modules), redirect_stdout(io.StringIO()):
            try:
                exec(setup_verification_code(), {})
            except ImportError as error:
                self.fail('Setup verification imported the wrong backend: ' + str(error))
        loader.assert_not_called()

    def test_setup_verification_fails_without_faster_whisper(self):
        modules = {'torch': fake_torch(), 'faster_whisper': None, 'whisper': None}
        with patch.dict(sys.modules, modules), redirect_stdout(io.StringIO()):
            with self.assertRaises(ImportError) as error:
                exec(setup_verification_code(), {})
        self.assertEqual(error.exception.name, 'faster_whisper')


if __name__ == '__main__':
    unittest.main()
