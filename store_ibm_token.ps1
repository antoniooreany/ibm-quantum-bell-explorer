# ------------------------------------------------------------
    # 1️⃣ Prompt for the token (input hidden)
    # ------------------------------------------------------------
    $secureToken = Read-Host -AsSecureString `
        "🔑 Enter your IBM Quantum token (input will be hidden)"

    # ------------------------------------------------------------
    # 2️⃣ Convert the SecureString to plain text **only in memory**
    # ------------------------------------------------------------
    $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    $plainToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($ptr)

    # Clean‑up the BSTR so the secret isn’t left in memory
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)

    # ------------------------------------------------------------
    # 3️⃣ Store the token as a generic credential
    #    (key = IBM_QUANTUM_TOKEN, user = IBM_QUANTUM_TOKEN)
    # ------------------------------------------------------------
    cmdkey /generic:"IBM_QUANTUM_TOKEN" `
           /user:"IBM_QUANTUM_TOKEN" `
           /pass:"$plainToken"

    # ------------------------------------------------------------
    # 4️⃣ (Optional) Export to the current PowerShell session
    # ------------------------------------------------------------
    $env:IBM_QUANTUM_TOKEN = $plainToken   # available only for this session

    # ------------------------------------------------------------
    # 5️⃣ Confirmation
    # ------------------------------------------------------------
    Write-Host "✅ Token securely saved to Windows Credential Manager."
    # To remove later: cmdkey /delete:"IBM_QUANTUM_TOKEN"