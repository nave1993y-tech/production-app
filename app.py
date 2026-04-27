<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Production App</title>

<style>
body {
    font-family: Arial;
    background: #f5f7fb;
    padding: 10px;
}

.container {
    background: white;
    padding: 15px;
    border-radius: 10px;
}

h1 {
    text-align: center;
    color: #1f4e79;
}

/* GRID */
.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}

input {
    width: 100%;
    padding: 8px;
    border-radius: 8px;
    border: 1px solid #ccc;
}

/* BUTTONS */
.btn {
    padding: 10px;
    border: none;
    border-radius: 8px;
    color: white;
    width: 100%;
    font-weight: bold;
}

.save { background: green; }
.reset { background: red; }

/* TABLE */
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th, td {
    border: 1px solid #ddd;
    padding: 6px;
    font-size: 12px;
}

th {
    background: #dbe5f1;
}

/* ACTION BUTTONS */
.edit { background: blue; color: white; }
.delete { background: red; color: white; }

/* DOWNLOAD */
.download {
    background: purple;
    margin-top: 20px;
}
</style>
</head>

<body>

<div class="container">

<h1>Daily production Day and Night</h1>

<div class="grid">
<input placeholder="S.no" id="sno">
<input placeholder="Day/Night" id="shift">
<input placeholder="Machine" id="machine">

<input placeholder="Size" id="size">
<input placeholder="Board Type" id="board">
<input placeholder="Thickness" id="thickness">

<input placeholder="Paper" id="paper">
<input placeholder="Finish" id="finish">
<input placeholder="OSR" id="osr">

<input placeholder="A Grade" id="a">
<input placeholder="B Grade" id="b">
<input placeholder="Qty" id="qty">
</div>

<br>

<button class="btn save" onclick="saveData()">SAVE</button>
<button class="btn reset" onclick="resetData()">RESET</button>

<h3>Saved Entries</h3>

<table id="table">
<tr>
<th>S.no</th>
<th>Shift</th>
<th>Machine</th>
<th>Size</th>
<th>Board</th>
<th>Thickness</th>
<th>Paper</th>
<th>Finish</th>
<th>OSR</th>
<th>A</th>
<th>B</th>
<th>Qty</th>
<th>Action</th>
</tr>
</table>

<button class="btn download" onclick="downloadCSV()">Download Excel</button>

</div>

<script>
let data = [];

function saveData() {
    let row = {
        sno: sno.value,
        shift: shift.value,
        machine: machine.value,
        size: size.value,
        board: board.value,
        thickness: thickness.value,
        paper: paper.value,
        finish: finish.value,
        osr: osr.value,
        a: a.value,
        b: b.value,
        qty: qty.value
    };

    data.push(row);
    renderTable();
}

function renderTable() {
    let table = document.getElementById("table");
    table.innerHTML = table.rows[0].outerHTML;

    data.forEach((d, i) => {
        let row = table.insertRow();

        row.innerHTML = `
        <td>${d.sno}</td>
        <td>${d.shift}</td>
        <td>${d.machine}</td>
        <td>${d.size}</td>
        <td>${d.board}</td>
        <td>${d.thickness}</td>
        <td>${d.paper}</td>
        <td>${d.finish}</td>
        <td>${d.osr}</td>
        <td>${d.a}</td>
        <td>${d.b}</td>
        <td>${d.qty}</td>
        <td>
            <button class="edit" onclick="editRow(${i})">Edit</button>
            <button class="delete" onclick="deleteRow(${i})">Delete</button>
        </td>
        `;
    });
}

function deleteRow(i) {
    data.splice(i, 1);
    renderTable();
}

function editRow(i) {
    let d = data[i];

    sno.value = d.sno;
    shift.value = d.shift;
    machine.value = d.machine;
    size.value = d.size;
    board.value = d.board;
    thickness.value = d.thickness;
    paper.value = d.paper;
    finish.value = d.finish;
    osr.value = d.osr;
    a.value = d.a;
    b.value = d.b;
    qty.value = d.qty;

    deleteRow(i);
}

function resetData() {
    data = [];
    renderTable();
}

function downloadCSV() {
    let csv = "Sno,Shift,Machine,Size,Board,Thickness,Paper,Finish,OSR,A,B,Qty\n";

    data.forEach(d => {
        csv += `${d.sno},${d.shift},${d.machine},${d.size},${d.board},${d.thickness},${d.paper},${d.finish},${d.osr},${d.a},${d.b},${d.qty}\n`;
    });

    let blob = new Blob([csv]);
    let a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "production.csv";
    a.click();
}
</script>

</body>
</html>
