*** Settings ***
Library    tipo_cambio.py

*** Test Cases ***
Registrar Tipo de cambio
    ${value}=    Tipo de Cambio
    Set Test Message    message=${value}
