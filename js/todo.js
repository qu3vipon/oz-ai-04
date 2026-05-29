const todoInput = document.querySelector("#todo-input");
const addBtn = document.querySelector("#add-btn");
const todoList = document.querySelector("#todo-list");

let todos = [];

const savedTodos = JSON.parse(localStorage.getItem("todos"));
if (savedTodos) {
    todos = savedTodos;
    renderTodos();
}

// 전체 todos 목록을 화면에 그리는 함수
function renderTodos() {
    todoList.innerHTML = "";

    for (const todo of todos) {
        const li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center";
        li.textContent = todo;
        todoList.appendChild(li);
    };
};

function addTodo() {
    const todo = todoInput.value.trim();
    if (todo === "") {
        alert("할 일을 입력하세요.")
        return;
    }

    todos.push(todo);
    console.log(todos);
    localStorage.setItem("todos", JSON.stringify(todos));
    todoInput.value = "";
    renderTodos();
}

addBtn.addEventListener("click", addTodo);
