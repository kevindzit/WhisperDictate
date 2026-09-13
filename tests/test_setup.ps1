$ErrorActionPreference = 'Stop'
$repoPath = Split-Path -Parent $PSScriptRoot
$setupPath = Join-Path $repoPath 'setup.ps1'

$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $setupPath, [ref]$tokens, [ref]$parseErrors
)
if ($parseErrors.Count -gt 0) {
    throw "setup.ps1 has syntax errors: $($parseErrors -join '; ')"
}

$verification = $ast.Find({
    param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $node.Name -eq 'Confirm-WhisperInstallation'
}, $true)
if ($null -eq $verification) {
    throw 'Could not find Confirm-WhisperInstallation in setup.ps1.'
}

# Load only the verification function, without running installation or startup steps
. ([scriptblock]::Create($verification.Extent.Text))
$pythonPath = (Get-Command python -CommandType Application | Select-Object -First 1).Source
$testPath = Join-Path ([IO.Path]::GetTempPath()) ('whisper-setup-test-' + [guid]::NewGuid())
[IO.Directory]::CreateDirectory($testPath) | Out-Null
$previousPythonPath = $env:PYTHONPATH
$utf8 = [System.Text.UTF8Encoding]::new($false)

try {
    $torchStub = @'
__version__ = "test"
class cuda:
    @staticmethod
    def is_available():
        return False
'@
    [IO.File]::WriteAllText((Join-Path $testPath 'torch.py'), $torchStub, $utf8)
    [IO.File]::WriteAllText(
        (Join-Path $testPath 'faster_whisper.py'), "class WhisperModel: pass`n", $utf8
    )
    [IO.File]::WriteAllText(
        (Join-Path $testPath 'whisper.py'), "raise ImportError('legacy backend must not be used')`n", $utf8
    )
    $env:PYTHONPATH = $testPath

    Confirm-WhisperInstallation -PythonPath $pythonPath
    Write-Host 'PASS: setup verifies faster-whisper without loading a model.'

    [IO.File]::WriteAllText(
        (Join-Path $testPath 'faster_whisper.py'), "raise ImportError('test backend failure')`n", $utf8
    )
    $failed = $false
    try {
        Confirm-WhisperInstallation -PythonPath $pythonPath
    } catch {
        $failed = $true
    }
    if (-not $failed) {
        throw 'Verification did not stop after Python returned an error.'
    }
    Write-Host 'PASS: a failed Python verification stops setup.'
} finally {
    $env:PYTHONPATH = $previousPythonPath
    Remove-Item -LiteralPath $testPath -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host 'PowerShell setup checks passed.'
exit 0
