// 객체(object)

let user = {
    name: "alex",
    age: 30
}

console.log(user.name);
console.log(user["age"]);

for (const key in user) {
    console.log(key, user[key]);
}