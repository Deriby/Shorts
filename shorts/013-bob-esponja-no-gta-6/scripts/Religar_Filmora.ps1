$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$root = [IO.Path]::GetFullPath($env:MASSACOTE_FILMORA_ROOT)
$stem = 'Bob_Esponja_no_GTA_6_16x9_R2'
$base = Join-Path $root 'Base_da_edicao.dat'
$target = Join-Path $root ($stem + '_Local.wfp')
$stage = Join-Path $root ([Guid]::NewGuid().ToString() + '.tmp')
function Abrir([string]$path) {
    Write-Host ('Projeto: ' + $path)
    if ($env:MASSACOTE_FILMORA_VERIFICAR -ne '1') {
        try { Start-Process -FilePath $path } catch { Write-Host 'Abra o WFP indicado no Filmora.' }
    }
}
function Texto($entry) {
    $reader = New-Object IO.StreamReader($entry.Open())
    try { $reader.ReadToEnd() } finally { $reader.Dispose() }
}
function Json([string]$v) { ConvertTo-Json -InputObject $v -Compress }
try {
    if (!(Test-Path -LiteralPath $base -PathType Leaf)) { throw 'Extraia o ZIP inteiro em uma pasta antes de abrir.' }
    if (Test-Path -LiteralPath $target -PathType Leaf) { Abrir $target; exit 0 }
    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [IO.Compression.ZipFile]::OpenRead($base)
    try {
        $lib = $archive.GetEntry('ProjectFolder/Medias/medias_info.json')
        if ($null -eq $lib) { throw 'O WFP do pacote esta incompleto.' }
        # The native media_structure repeats keys; parse only the media_items object.
        $catalog = Texto $lib
        $quote = [string][char]34
        $position = $catalog.IndexOf($quote + 'media_items' + $quote + ':',[StringComparison]::Ordinal)
        if ($position -lt 0) { throw 'O catalogo de midias do WFP esta incompleto.' }
        $mediaJson = '{' + $catalog.Substring($position)
        $items = (ConvertFrom-Json -InputObject $mediaJson).media_items.PSObject.Properties
        $paths = @{}
        foreach ($item in $items) {
            $relative = [string]$item.Value.download_url
            if (!$relative.StartsWith('./midias/')) { continue }
            if ($relative -notmatch '^\./midias/[a-zA-Z0-9_.-]+$') { throw ('Referencia inesperada: ' + $relative) }
            $asset = Join-Path $root $relative.Substring(2)
            if (!(Test-Path -LiteralPath $asset -PathType Leaf)) { throw ('Midia faltando: ' + $relative) }
            if ((Get-FileHash -LiteralPath $asset -Algorithm MD5).Hash -ne $item.Value.src_md5) { throw ('Midia diferente da incluida no ZIP: ' + $relative) }
            $paths[$relative] = [IO.Path]::GetFullPath($asset).Replace([char]92,[char]47)
        }
        if ($paths.Count -ne 41) { throw 'O projeto deveria apontar para 41 midias.' }
        $result = [IO.Compression.ZipFile]::Open($stage,[IO.Compression.ZipArchiveMode]::Create)
        try {
            $utf = New-Object Text.UTF8Encoding($false)
            foreach ($entry in $archive.Entries) {
                $dest = $result.CreateEntry($entry.FullName,[IO.Compression.CompressionLevel]::NoCompression)
                $stream = $dest.Open()
                try {
                    if ($entry.FullName -match '\.(json|wesproj)$') {
                        $body = Texto $entry
                        foreach ($rel in $paths.Keys) {
                            $absolute = $paths[$rel]
                            if ($absolute.StartsWith('/')) { $uri = 'file:' + $absolute } else { $uri = 'file:/' + $absolute }
                            $body = $body.Replace((Json ('file:' + $rel)),(Json $uri)).Replace((Json $rel),(Json $absolute))
                        }
                        if ($body.Contains('./midias/')) { throw ('Vinculo relativo restante em ' + $entry.FullName) }
                        if ($entry.FullName -match '(timeline\.wesproj|project_info\.json)$') {
                            $body = $body.Replace((Json $stem),(Json ($stem + '_Local'))).Replace((Json ($stem + '.wfp')),(Json ($stem + '_Local.wfp')))
                        }
                        if ($entry.FullName -eq 'ProjectFolder/project_info.json') {
                            $guid = (ConvertFrom-Json -InputObject $body).project_guid
                            if ($guid) { $body = $body.Replace((Json $guid),(Json ([Guid]::NewGuid().ToString('B').ToUpperInvariant()))) }
                        }
                        $bytes = $utf.GetBytes($body)
                        $stream.Write($bytes,0,$bytes.Length)
                    } else {
                        $original = $entry.Open()
                        try { $original.CopyTo($stream) } finally { $original.Dispose() }
                    }
                } finally { $stream.Dispose() }
            }
        } finally { $result.Dispose() }
    } finally { $archive.Dispose() }
    [IO.File]::Move($stage,$target)
    Abrir $target
} catch {
    Write-Host $_.Exception.Message
    exit 1
} finally {
    if (Test-Path -LiteralPath $stage -PathType Leaf) { Remove-Item -LiteralPath $stage }
}
