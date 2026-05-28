@echo off

cd /d "C:\Users\b.souza\OneDrive - Alvarez and Marsal\Documents\Alvarez & Marsal\GERDAU\Manual_CMG\Report_GitHub"

echo =====================================
echo Atualizando Dashboard CMG...
echo =====================================

echo Sincronizando com GitHub...
git pull origin main

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