# 当前脚本所在目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$sourceFile = Join-Path $scriptDir "swallowing_star.txt"
$outputDir = Join-Path $scriptDir "split"

$parts = 100

# GB2312 编码读取
$gb2312 = [System.Text.Encoding]::GetEncoding("GB2312")


Write-Host "读取文件..."

$content = [System.IO.File]::ReadAllText(
    $sourceFile,
    $gb2312
)


$totalLength = $content.Length

Write-Host "总字符数: $totalLength"


# 创建输出目录
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}


$chunkSize = [Math]::Ceiling($totalLength / $parts)

Write-Host "每份字符数: $chunkSize"


# UTF-8 无 BOM
$utf8 = New-Object System.Text.UTF8Encoding($false)


for ($i = 0; $i -lt $parts; $i++) {

    $start = $i * $chunkSize


    if ($start -ge $totalLength) {
        break
    }


    $length = [Math]::Min(
        $chunkSize,
        $totalLength - $start
    )


    $partContent = $content.Substring(
        $start,
        $length
    )


    $fileName = Join-Path `
        $outputDir `
        ("part_{0:D3}.txt" -f ($i + 1))


    [System.IO.File]::WriteAllText(
        $fileName,
        $partContent,
        $utf8
    )


    Write-Host "生成: $fileName"
}


Write-Host ""
Write-Host "拆分完成!"