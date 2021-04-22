@echo off

for %%I in (%*) do (
echo %%I
python "%~dp0\pyscripts\unpack_spk.py" %%I
echo.
)
