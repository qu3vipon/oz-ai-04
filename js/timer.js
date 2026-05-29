// setTimeout
// 일정 시간이 지나면, 어떤 함수를 실행할 수 있게 함수

// setTimeout(
//     () => console.log("3초가 지났습니다"),
//     3000  // 1ms = 1/1000s
// );

// setInterval
// 일정 시간마다 함수를 반복 실행하는 함수
let count = 0;

const timerId = setInterval(
    () => {
        count++;
        console.log(count + '번째 호출');

        if (count == 5) {
            clearInterval(timerId);
        };
    }, 1000
);
