// 获取按键选择器
const getSelector = () => {
    let selector = ''
    // 区分 shift alt control 左右键
    if ([16, 17, 18].includes(event.keyCode)) {
        selector = `#k${event.keyCode}${event.code.endsWith('Left') ? '_left' : '_right'}`
    } else {
        // 区分 enter 键
        if (event.keyCode === 13 && event.code === 'NumpadEnter') {
            selector = `#k${event.keyCode}_num` // 数字小键盘中的 enter 键
        } else {
            selector = `#k${event.keyCode}`
        }
    }
    return selector
}

// 按下
document.addEventListener('keydown', (event) => {
    const key = document.querySelector(getSelector())
    key && key.classList.add('active')
})

// 松开
document.addEventListener('keyup', (event) => {
    const key = document.querySelector(getSelector())
    if (key) {
        key.classList.remove('active')

        // 坐标点
        const position = key.getBoundingClientRect()
        const x = position.left
        const y = position.top

        // 宽 高
        const w = key.offsetWidth
        const h = key.offsetHeight

        // 创建元素并设置样式
        const div = document.createElement('div')
        div.className = 'key-bubble'
        div.innerText = event.key === ' ' ? 'SPACE' : event.key.toLocaleUpperCase();
        div.style.cssText = `
                    left: ${x}px;
                    top: ${y}px;
                    opacity: .6;
                    width: ${w}px;
                    height: ${h}px;
                `
        document.body.append(div)

        // 100 毫秒后改变位置
        setTimeout(() => {
            div.style.cssText = `
                        left: ${x}px;
                        top: ${y - 500}px;
                        opacity: 0;
                        width: ${w}px;
                        height: ${h}px;
                    `
            setTimeout(() => div.remove(), 2050)
        }, 100)
    }
})


// 获取按键选择器
function getId(vk, flag) {
    let selector = '';
    selector = `k${vk}`;
    if (vk == 160) {
        selector = `k16_left`;
    } else if (vk == 161) {
        selector = `k16_right`;
    } else if (vk == 162) {
        selector = `k17_left`;
    } else if (vk == 163) {
        selector = `k17_right`;
    } else if (vk == 164) {
        selector = `k18_left`;
    } else if (vk == 165) {
        selector = `k18_right`;
    }
    return selector;
}

