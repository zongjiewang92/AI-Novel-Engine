# 统计字数, 在 当前目录下执行
$text = Get-Content .\chapter0002.md -Raw; ($text.ToCharArray() | Where-Object { $_ -match '[\u4e00-\u9fff]' }).Count