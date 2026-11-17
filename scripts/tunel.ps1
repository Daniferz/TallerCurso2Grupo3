param(
    [Parameter(Position = 0)]
    [ValidateRange(1, 65535)]
    [int]$Puerto = 8000
)

$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if ($null -eq $cloudflared) {
    Write-Host "No se encontró cloudflared." -ForegroundColor Yellow
    Write-Host "Instalación recomendada: winget install Cloudflare.cloudflared"
    Write-Host "Si winget no está disponible, descarga el ejecutable oficial x64:"
    Write-Host "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    Write-Host "Después ejecútalo desde la carpeta de descarga: .\cloudflared-windows-amd64.exe tunnel --url http://127.0.0.1:$Puerto"
    exit 1
}

$urlLocal = "http://127.0.0.1:$Puerto"
Write-Host "Abriendo un túnel de Cloudflare hacia $urlLocal."
Write-Host "Deja esta terminal abierta mientras tus compañeros prueban el agente."
$ultimaUrl = ""

& $cloudflared.Source tunnel --url $urlLocal 2>&1 | ForEach-Object {
    $linea = $_.ToString()
    Write-Host $linea
    $coincidencia = [regex]::Match($linea, 'https://[A-Za-z0-9-]+\.trycloudflare\.com')
    if ($coincidencia.Success -and $coincidencia.Value -ne $ultimaUrl) {
        $ultimaUrl = $coincidencia.Value
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host " URL PUBLICA: $ultimaUrl" -ForegroundColor Cyan
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host "Pega esta dirección en URL_PUBLICA de tu .env y reinicia tu agente; pásasela a tu compañero para que la ponga en su URLS_AGENTES." -ForegroundColor Yellow
        Write-Host ""
    }
}
