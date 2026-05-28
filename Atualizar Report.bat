@echo off
cd /d "C:\Users\b.souza\OneDrive - Alvarez and Marsal\Documents\Alvarez & Marsal\GERDAU\Manual_CMG\Report_GitHub"

echo =====================================
echo Atualizando Dashboard CMG...
echo =====================================

git add .

git commit -m "Atualizacao automatica dashboard"

git push

echo.
echo =====================================
echo Dashboard enviado ao GitHub!
echo Aguarde 1-3 minutos para atualizar.
echo =====================================

pause