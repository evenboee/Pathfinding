// const WIDTH = window.innerWidth;
// const HEIGHT = window.innerHeight;
const gscl = 50;
// const w = Math.floor(WIDTH / gscl);
// const h = Math.floor(HEIGHT / gscl);// w * 13 / 20;
const w = 20;
const h = 15;
const WIDTH = gscl * w;
const HEIGHT = gscl * h;
const maxNode = w * h;
const wall = 0;

let h_mode = "M"; // "E"

let start = 0;
let target = 115;

let rMouseDown = false;
let lMouseDown = false;
let brushSize = 1;

function makeMatrix() {
	const filler = new Array(w + 2).fill(wall);
	let m = [];
	m.push(filler);
	for (let i = 0; i < h; i++) {
		let row = new Array(w + 2).fill(1);
		row[0] = row[row.length - 1] = wall;
		m.push(row);
	}
	m.push(filler);
	return m;
}

let matrix = makeMatrix();
matrix[1][4] = matrix[2][4] = matrix[3][4] = matrix[4][4] = matrix[5][4] = wall;


function nToPos(n) {
	return [n % w, Math.floor(n / w)];
}

function nToMatrixIndex(n) {
	const pos = nToPos(n);
	return [pos[0] + 1, pos[1] + 1];
}

let h_multi = 1.0

function getHCost(n, diagonal=false) {
	const tPos = nToPos(target);
	const nPos = nToPos(n);
	if (h_mode == "M") return h_multi * Math.abs(tPos[0] - nPos[0]) + Math.abs(tPos[1] - nPos[1]);
	else if (h_mode == "E") return h_multi * Math.sqrt(Math.pow(tPos[0] - nPos[0], 2) + Math.pow(tPos[1] - nPos[1], 2));
	return 0;
}

// .find() noe som ikke finnes => undefined
function findPath() {
	let steps = [];
	const startEntry = [start, -1, 0, start];
	let open = [startEntry]; // Entry = [ID, f_cost, g_cost, parent]
	let closed = [];

	while (open.length != 0) {
		open.sort((a, b) => a[1] - b[1]);
		const current = open.shift();
		const currentIndex = nToMatrixIndex(current[0]);
		closed.push(current);

		if (current[0] == target) break;

		const neighbors = [ // Entry: [number, [matrixX, matrixY]]
			[current[0] + 1, [currentIndex[0] + 1, currentIndex[1]]],
			[current[0] - 1, [currentIndex[0] - 1, currentIndex[1]]],
			[current[0] + w, [currentIndex[0], currentIndex[1] + 1]],
			[current[0] - w, [currentIndex[0], currentIndex[1] - 1]]
		];
		for (let i in neighbors) {
			const n = neighbors[i][0];
			const nIndex = neighbors[i][1];
			
			if (matrix[nIndex[1]][nIndex[0]] == wall || closed.find(q => (q[0] === n)) != undefined) continue;

			const nInOpen = open.find(q => (q[0] === n));
			const g_cost = current[2] + 1;
			const h_cost = getHCost(n);
			const f_cost = g_cost + h_cost;
			if (nInOpen == undefined) {	
				open.push([n, f_cost, g_cost, current[0]]);
			}
			else if (nInOpen[2] < g_cost) {
				const index = open.indexOf(nInOpen);
				open[index][1] = f_cost;
				open[index][2] = g_cost;
				open[index][3] = current[0];
			}
		}
		steps.push([Array.from(open), Array.from(closed)]);
	}

	let solution = [];
	let g = closed[closed.length - 1];
	if (g[0] != target) return [solution, steps];
	while (g[0] != g[3]) {// StartEntry has same ID as parent
		solution.push(g);
		g = closed.find(q => (q[0] === g[3]));
	}
	return [solution.reverse(), steps];
}


// const scl = [WIDTH / w, HEIGHT / h];
const scl = [gscl, gscl];
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext("2d");
let interval;

window.onload = () => {
	document.getElementById("solve").onclick = solve;
	document.getElementById("animate").onclick = animate;
	document.getElementById("clear").onclick = () => draw();

	document.getElementById("multiplier").oninput = () => {
		const val = parseFloat(document.getElementById("multiplier").value).toFixed(1);
		update_h_multiplier(val);
	}

	document.getElementById("supergreedy").onclick = () => {update_h_multiplier(100);}

	const radios = document.querySelectorAll("input[type='radio']");
	for (let r in radios) {
		radios[r].onchange = setHMode;
	}

	canvas.width = WIDTH;
	canvas.height = HEIGHT;

	document.getElementById("canvas").onmousedown = e => {
		if (e.button == 0) {
			lMouseDown = true;
		} else if(e.button == 2) {
			rMouseDown = true;
		}
	}

	document.getElementById("canvas").onmousemove = e => {
		paint(e.offsetX, e.offsetY);
	}

	document.onmouseup = e => {
		if (e.button == 0) {
			lMouseDown = false;
		} else if(e.button == 2) {
			rMouseDown = false;
		}
	}

	draw();
}


function setHMode() {
	const checked = document.querySelector("input[name='h_mode']:checked");
	h_mode = checked.value;
}

function update_h_multiplier(newValue) {
	document.getElementById("multiplier-display").innerHTML = newValue;
	h_multi = newValue;
}

function paint(x, y) {
	if (lMouseDown || rMouseDown) {
		let paintvalue = (lMouseDown ? wall : 1);
		const xy = [Math.floor(x / gscl), Math.floor(y / gscl)];
		matrix[xy[1] + 1][xy[0] + 1] = paintvalue;
		draw();
	}
}


function solve() {
	const s = findPath()[0];
	draw(s);
}


function draw(solution=[], step=null) {
	available = false;
	ctx.fillStyle = "#333";
	ctx.fillRect(0, 0, WIDTH, HEIGHT);

	if (step != null) {
		const open = step[0];
		const closed = step[1];

		drawAllinArray(closed, "#000");
		drawAllinArray(open, "#666");
	}

	drawAllinArray(solution, "#33f");

	ctx.fillStyle = "#f1f1f1";
	for (let y = 1; y < matrix.length - 1; y++) {
		for (let x = 1; x < matrix[y].length - 1; x++) {
			if (matrix[y][x] == wall)
				ctx.fillRect((x - 1) * scl[0] + 1, (y - 1) * scl[1] + 1, scl[0] - 2, scl[1] - 2);
		}
	}

	const startPos = nToPos(start);
	ctx.fillStyle = "#f33";
	ctx.fillRect(startPos[0] * scl[0] + 1, startPos[1] * scl[1] + 1, scl[0] - 2, scl[1] - 2);

	const targetPos = nToPos(target);
	ctx.fillStyle = "#3f3";
	ctx.fillRect(targetPos[0] * scl[0] + 1, targetPos[1] * scl[1] + 1, scl[0] - 2, scl[1] - 2);
}

function drawAllinArray(arr, color) {
	ctx.fillStyle = color;
	for (let i in arr) {
		const n = nToPos(arr[i][0]);
		ctx.fillRect(n[0] * scl[0] + 1, n[1] * scl[1] + 1, scl[0] - 2, scl[1] - 2);
	}
}

async function animate() {
	const solution = findPath();
	const steps = solution[1];
	const path = solution[0];
	const steptime = 50 // 2000 / steps.length;
	for (let i in steps) {
		draw([], steps[i]);
		await sleep(steptime);
	}
	if (solution.length > 0) draw(path, steps[steps.length - 1]);
	else console.log("No path found");
}

function drawStep(step) {
	draw([], step);
}

const sleep = ms => new Promise(r => setTimeout(r, ms));