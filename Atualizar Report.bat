@echo off

cd /d "C:\Users\b.souza\Alvarez and Marsal\[GERDAU] Implantação de PMO - Reports GERDAU\Geotecnia de Inspeção\Report_ManualCMG"

echo =====================================
echo Atualizando Dashboard CMG...
echo =====================================

echo Sincronizando com GitHub...
git pull origin main --rebase

echo Enviando atualizacoes...
git add .

git commit -m "Atualizacao automatica dashboard"

git push origin main

echo.
echo =====================================
echo Dashboard atualizado!
echo Aguarde 1-3 minutos.
echo =====================================

pause