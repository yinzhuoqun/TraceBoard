const backgroundColor = document.getElementById('backgroundColor');
const colorKey = document.getElementById('colorKey');
const nickname = document.getElementById('nickname');

window.addEventListener('load', () => {
    const storedBackgroundColor = localStorage.getItem('backgroundColor');
    if (storedBackgroundColor) {
        document.querySelector('.container').style.backgroundColor = storedBackgroundColor;
        backgroundColor.value = storedBackgroundColor;
    }

    const storedKeyColor = localStorage.getItem('keyColor');
    colorKey.value = storedKeyColor;
    if (storedKeyColor) {
        document.querySelectorAll('.key').forEach(key => {
            key.style.backgroundColor = storedKeyColor;
        });
    }

    // const storedNickname = localStorage.getItem('nickname');
    // if (storedNickname) {
    //     nickname.value = storedNickname;
    // }

});

backgroundColor.addEventListener('input', (event) => {
    const selectedColor = event.target.value;
    document.querySelector('.container').style.backgroundColor = selectedColor; // 改背景
    localStorage.setItem('backgroundColor', selectedColor);
});


colorKey.addEventListener('input', (event) => {
    const selectedColor = event.target.value;
    localStorage.setItem('keyColor', selectedColor);
    document.querySelectorAll('.key').forEach(key => {
        key.style.backgroundColor = selectedColor; // 改按键
    });
});


nickname.addEventListener('input', (event) => {
    const selectedNickname = event.target.value;
    localStorage.setItem('nickname', selectedNickname);
    nickname.value = selectedNickname; // 改昵称
    save_nickname(selectedNickname).then(r => {
    });
});


async function save_nickname(nickname) {
    try {
        const response = await fetch('http://127.0.0.1:21315/save_nickname', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify({nickname}) // 将对象序列化为 JSON 字符串
        });
        const result = await response.json();
    } catch (error) {
        console.error('Error saving nickname:', error);
    }
}


async function get_rank_list() {
    // try {
    const response = await fetch('http://tb.zhuoqun.info:5000/trace_board_data/');
    const result = await response.json();
    const ol = document.querySelector('.rank-list ol')
    ol.innerHTML = ''; // 清空现有内容
    result.data.forEach(item => {
        const li = document.createElement('li');
        // console.log(item.virtual_key_code);
        li.textContent = `${item.nickname} ⌨ ${item.count}次`;
        ol.appendChild(li);
    });
    // } catch (error) {
    //     console.error('Error saving nickname:', error);
    // }
}


const tooltip = document.getElementById('tooltip');

// 获取按键点击次数并设置热力图
async function fetchKeyCounts() {
    try {
        const response = await fetch('http://127.0.0.1:21315/key_counts');
        const responseData = await response.json();
        const keyCounts = responseData.data;
        nickname.value = responseData.nickname;
        // 获取最大按键点击次数
        const maxCount = Math.max(...keyCounts.map(item => item.count));
        keyCounts.forEach(item => {
            const id_ = getId(item.virtual_key_code, item.key_name);
            const keyElement = document.getElementById(id_);
            if (keyElement) {
                const count = item.count;
                keyElement.style.backgroundColor = generateRGBColors(count, maxCount); // 根据点击量改变键盘按键颜色
                keyElement.addEventListener('mouseover', function (event) {
                    tooltip.textContent = `您一共按了 ${item.count} 次`;
                    tooltip.style.display = 'block';
                    tooltip.style.left = event.pageX + 10 + 'px';  // Position tooltip next to mouse
                    tooltip.style.top = event.pageY + 10 + 'px';
                });

                keyElement.addEventListener('mousemove', function (event) {
                    tooltip.style.left = event.pageX + 10 + 'px';  // Update tooltip position
                    tooltip.style.top = event.pageY + 10 + 'px';
                });

                keyElement.addEventListener('mouseout', function () {
                    tooltip.style.display = 'none';
                });
            }
        });

        const top10Items = keyCounts.slice(0, 10);
        const ol = document.querySelector('.my-top-list ol')
        ol.innerHTML = ''; // 清空现有内容
        top10Items.forEach(item => {
            const li = document.createElement('li');
            // console.log(item.virtual_key_code);
            li.textContent = `${item.key_name} ⌨ ${item.count}次`;
            ol.appendChild(li);
        });

    } catch (error) {
        console.error('Error fetching key counts:', error);
    }
}

get_rank_list();
fetchKeyCounts();
// 每秒钟请求一次数据更新热力图
setInterval(fetchKeyCounts, 1500);
setInterval(get_rank_list, 1500);