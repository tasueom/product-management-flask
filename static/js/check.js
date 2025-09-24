function checkUser(f) {
    const username = f.username.value.trim();
    const email = f.email.value.trim();

    // 이름: 한글, 영문, 공백만 허용
    const nameRegex = /^[가-힣a-zA-Z\s]+$/;
    if (!nameRegex.test(username)) {
        alert("이름은 한글, 영문, 공백만 입력 가능합니다.");
        f.username.focus();
        return false;
    }

    // 이메일: 입력되었다면 형식 검사
    if (email !== "") {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert("올바른 이메일 주소를 입력하세요.");
            f.email.focus();
            return false;
        }
    }

    return true;
}

function checkProduct(f) {
    const price = f.price.value.trim();
    const stock = f.stock.value.trim();

    // 가격: 숫자, 1 이상
    if (isNaN(price) || Number(price) < 1) {
        alert("가격은 1 이상의 숫자로 입력하세요.");
        f.price.focus();
        return false;
    }

    // 재고: 숫자, 1 이상
    if (isNaN(stock) || Number(stock) < 0) {
        alert("재고는 0 이상의 숫자로 입력하세요.");
        f.stock.focus();
        return false;
    }

    return true;
}
