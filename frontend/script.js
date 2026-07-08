const API = "/api";

/* ------------------------- */
/* Helpers */
/* ------------------------- */

function authHeader() {
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + localStorage.getItem("token")
    };
}

function showMessage(id, message, color = "#b00020") {
    const element = document.getElementById(id);

    if (element) {
        element.style.color = color;
        element.innerText = message;
    }
}

/* ------------------------- */
/* LOGIN */
/* ------------------------- */

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async (e) => {

        e.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {

            const response = await fetch(API + "/login", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email,
                    password
                })

            });

            const data = await response.json();

            if (response.ok) {

                localStorage.setItem("token", data.token);
                localStorage.setItem("name", data.name);
                localStorage.setItem("account", data.account_number);

                window.location.href = "dashboard.html";

            } else {

                showMessage("message", data.message);

            }

        } catch {

            showMessage("message", "Server unavailable.");

        }

    });

}

/* ------------------------- */
/* REGISTER */
/* ------------------------- */

const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", async (e) => {

        e.preventDefault();

        const full_name = document.getElementById("fullname").value;
        const email = document.getElementById("regEmail").value;
        const password = document.getElementById("regPassword").value;

        try {

            const response = await fetch(API + "/register", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    full_name,
                    email,
                    password

                })

            });

            const data = await response.json();

            if (response.ok) {

                showMessage(
                    "message",
                    "Registration Successful. Redirecting...",
                    "green"
                );

                setTimeout(() => {

                    window.location.href = "index.html";

                }, 2000);

            } else {

                showMessage("message", data.message);

            }

        } catch {

            showMessage("message", "Server unavailable.");

        }

    });

}

/* ------------------------- */
/* BALANCE */
/* ------------------------- */

async function loadBalance() {

    try {

        const response = await fetch(API + "/balance", {

            headers: authHeader()

        });

        if (!response.ok)
            return;

        const data = await response.json();

        document.getElementById("balance").innerText =
            "₹ " + Number(data.balance).toFixed(2);

        document.getElementById("accountNumber").innerText =
            data.account_number;

        document.getElementById("username").innerText =
            "Welcome, " + localStorage.getItem("name");

    } catch {

        console.log("Unable to load balance.");

    }

}

/* ------------------------- */
/* DEPOSIT */
/* ------------------------- */

async function depositMoney() {

    await performTransaction(

        "/deposit",

        {

            amount: document.getElementById("depositAmount").value,

            remarks: document.getElementById("depositRemark").value

        }

    );

}

/* ------------------------- */
/* WITHDRAW */
/* ------------------------- */

async function withdrawMoney() {

    await performTransaction(

        "/withdraw",

        {

            amount: document.getElementById("withdrawAmount").value,

            remarks: document.getElementById("withdrawRemark").value

        }

    );

}

/* ------------------------- */
/* TRANSFER */
/* ------------------------- */

async function transferMoney() {

    await performTransaction(

        "/transfer",

        {

            receiver_account: document.getElementById("receiverAccount").value,

            amount: document.getElementById("transferAmount").value,

            remarks: document.getElementById("transferRemark").value

        }

    );

}

/* ------------------------- */
/* COMMON TRANSACTION */
/* ------------------------- */

async function performTransaction(endpoint, payload) {

    try {

        const response = await fetch(API + endpoint, {

            method: "POST",

            headers: authHeader(),

            body: JSON.stringify(payload)

        });

        const data = await response.json();

        alert(data.message);

        if (response.ok) {

            loadBalance();

            loadHistory();

        }

    } catch {

        alert("Transaction Failed.");

    }

}

/* ------------------------- */
/* TRANSACTION HISTORY */
/* ------------------------- */

async function loadHistory() {

    try {

        const response = await fetch(API + "/transactions", {

            headers: authHeader()

        });

        if (!response.ok)
            return;

        const transactions = await response.json();

        const table = document.getElementById("historyBody");

        if (!table)
            return;

        table.innerHTML = "";

        transactions.forEach((transaction) => {

            table.innerHTML += `

            <tr>

                <td>${new Date(transaction.created_at).toLocaleString()}</td>

                <td>${transaction.transaction_type}</td>

                <td>₹ ${transaction.amount}</td>

                <td>${transaction.status}</td>

                <td>${transaction.reference_id}</td>

            </tr>

            `;

        });

    } catch {

        console.log("Unable to load transactions.");

    }

}

/* ------------------------- */
/* LOGOUT */
/* ------------------------- */

function logout() {

    localStorage.clear();

    window.location.href = "index.html";

}

/* ------------------------- */
/* DASHBOARD INIT */
/* ------------------------- */

if (window.location.pathname.includes("dashboard")) {

    loadBalance();

    loadHistory();

}