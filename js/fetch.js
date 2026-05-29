// GET 요청
// fetch("https://jsonplaceholder.typicode.com/posts")
//     .then(response => response.json())
//     .then(data => console.log(data));

// POST 요청
fetch("https://jsonplaceholder.typicode.com/posts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: "Python 공부법", body: "열심히 하세요." }),
})
    .then(response => response.json())
    .then(data => console.log(data));
