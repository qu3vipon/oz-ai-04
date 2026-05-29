// 배열(Array)
let numbers = [1, true, "hello", 50];

console.log(numbers)
console.log(numbers[0]);
console.log(numbers[1]);
console.log(numbers[2]);
console.log(numbers[3]);
console.log(numbers.at(-1));

let scores = [92, 100, 80, 79]

for (const [i, score] of scores.entries()) {
    console.log(i, score);
}
