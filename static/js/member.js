function homePage(){
    window.location.href = "/";
}

// Sing In / Sing Up
let btnSignupClose = document.getElementById("btn-signup-close");
let containerSignup = document.getElementById("signup-container");
let messageDivSignup = document.getElementById("message_signup");
let messageDivSignin = document.getElementById("message_signin");
let innerSignin = document.querySelector(".sign-in");
let innerSignup = document.querySelector(".sign-up");

btnSignupClose.addEventListener("click", () => {
    containerSignup.style.display = "none";
    innerSignin.classList.remove("show");
    messageDivSignup.style.display = "none";
    messageDivSignin.style.display = "none";
    innerSignup.style.height = "332px";
    innerSignin.style.height = "275px";
})
let btnSigninClose = document.getElementById("btn-signin-close");
let containerSignin = document.getElementById("signin-container");


btnSigninClose.addEventListener("click", () => {
    containerSignin.style.display = "none";
    innerSignin.classList.remove("show");
    messageDivSignup.style.display = "none";
    messageDivSignin.style.display = "none";
    innerSignup.style.height = "332px";
    innerSignin.style.height = "275px";
})
function handleClickSignin() {
    containerSignin.style.display = "flex";
    innerSignin.offsetWidth;
    innerSignin.classList.add("show");
}
let btnToSingupSingin = document.getElementById("sign-up-in");
btnToSingupSingin.addEventListener("click", handleClickSignin)

let btnSignInToSignUp = document.getElementById("sign-in-to-sign-up");
btnSignInToSignUp.addEventListener("click", () => {
    containerSignin.style.display = "none";
    containerSignup.style.display = "flex";
})

let btnSignUpToSignIn = document.getElementById("sign-up-to-sign-in");
btnSignUpToSignIn.addEventListener("click", () => {
    containerSignup.style.display = "none";
    containerSignin.style.display = "flex";
})

function submitSignIn() {
    event.preventDefault();
    let email=document.querySelector("input[name='signin_email']");
    let password=document.querySelector("input[name='signin_password']");
    let messageDiv = document.getElementById("message_signin");
    let signinContainer = document.querySelector(".sign-in");
    if(email.value === "" || password.value === ""){
        messageDiv.innerHTML =  "email、密碼不可為空"
        messageDiv.style.display = "flex";
        signinContainer.style.height = "315px";
        return false;
    } else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email.value)){
        messageDiv.innerHTML =  "email格式錯誤"
        messageDiv.style.display = "flex";
        signinContainer.style.height = "315px";
        return false;
    } else if (!/^(?=.*[A-Za-z])(?=.*\d).{8,20}$/.test(password.value)){
        messageDiv.innerHTML =  "密碼格式錯誤<br>(需包含字母與數字,且長度為8~20)"
        messageDiv.style.display = "flex";
        signinContainer.style.height = "339px";
        return false;
    }
    let formData = {
        "email": email.value,
        "password": password.value
    };
    let jsonData = JSON.stringify(formData);
    fetch("/api/user/auth", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: jsonData
    })
    .then(response => {
        if (response.status === 200) {
        return response.json().then(data => {
            localStorage.setItem("token", data.token);
            messageDiv.style.display = "none";
            signinContainer.style.height = "275px";
            setTimeout(() => {
                location.reload();
            }, 20);
            // messageDiv.innerHTML = "登入成功！3秒後自動重整";
            // messageDiv.style.display = "flex";
            // signinContainer.style.height = "315px";
            // setTimeout(() => {
            //     location.reload();
            // }, 3000);
        });
        } else if(response.status === 400) {
            return response.json().then(data => {
                messageDiv.innerHTML = data.message;
                messageDiv.style.display = "flex";
                signinContainer.style.height = "315px";
            });
        } else if(response.status === 500) {
            return response.json().then(data => {
                messageDiv.innerHTML = "伺服器內部錯誤，請稍後再試"
                messageDiv.style.display = "flex";
                signinContainer.style.height = "315px";
            });
        }
    })
    .catch(error => {
        console.error("錯誤：" + error);
    });
}

function submitSignUp() {
    event.preventDefault();
    let name=document.querySelector("input[name='signup_name']");
    let email=document.querySelector("input[name='signup_email']");
    let password=document.querySelector("input[name='signup_password']");
    let messageDiv = document.getElementById("message_signup");
    let signupContainer = document.querySelector(".sign-up");
    if(name.value === "" || email.value === "" || password.value === ""){
        messageDiv.innerHTML =  "姓名、email、密碼不可為空"
        messageDiv.style.display = "flex";
        signupContainer.style.height = "372px";
        return false;
    } else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email.value)){
        messageDiv.innerHTML =  "email格式錯誤"
        messageDiv.style.display = "flex";
        signupContainer.style.height = "372px";
        return false;
    } else if (!/^(?=.*[A-Za-z])(?=.*\d).{8,20}$/.test(password.value)){
        messageDiv.innerHTML =  "密碼格式錯誤<br>(需包含字母與數字,且長度為8~20)"
        messageDiv.style.display = "flex";
        signupContainer.style.height = "395px";
        return false;
    }
    let formData = {
        "name": name.value,
        "email": email.value,
        "password": password.value
    };
    let jsonData = JSON.stringify(formData);
    fetch("/api/user", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: jsonData
    })
    .then(response => {
        if (response.status === 200) {
            messageDiv.innerHTML = "註冊成功！5秒後自動返回登入頁<br>(未跳轉請手動點選)";
            messageDiv.style.display = "flex";
            signupContainer.style.height = "395px";
            setTimeout(function() {
                containerSignup.style.display = "none";
                containerSignin.style.display = "flex";
                messageDiv.style.display = "none";
                signupContainer.style.height = "332px";
            }, 5000); 
        } else if(response.status === 400) {
            return response.json().then(data => {
                messageDiv.innerHTML =  "註冊失敗，" + data.message;
                messageDiv.style.display = "flex";
                signupContainer.style.height = "372px";
            });
        } else if(response.status === 500) {
            return response.json().then(data => {
                messageDiv.innerHTML =  "註冊失敗，伺服器內部錯誤，請稍後再試";
                messageDiv.style.display = "flex";
                signupContainer.style.height = "372px";
            });
        }
    })
    .catch(error => {
        console.error("錯誤：" + error);
    });
}

function getSigninToken() {
    let token = localStorage.getItem("token");
    let singinSingout = document.getElementById("sign-up-in");
    if (token) {
        fetch("/api/user/auth", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    })
    .then(response => {
        if (response.status === 200) {
            return response;
        } else {
            console.error("請求錯誤：" + response.status);
        }
    })
    .then(() => {
        singinSingout.innerHTML = "登出系統"
        btnToSingupSingin.removeEventListener("click", handleClickSignin);
        btnToSingupSingin.addEventListener("click", handleClickSignout);
    })
    } else {
        console.log("oops");
    }
}
function handleClickSignout(){
    localStorage.removeItem("token");
        setTimeout(() => {
            location.reload();
        }, 20);
}

getSigninToken();