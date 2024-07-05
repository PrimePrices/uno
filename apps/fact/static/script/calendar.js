
// JavaScript to populate the calendar and handle clicks
const calendarBody = document.getElementById('calendar-body');
const daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
const today = new Date();
const currentMonth = today.getMonth();
const currentYear = today.getFullYear();
const firstDayOfMonth = 1
const daysInPrevMonth = daysInMonth[currentMonth === 0 ? 11 : currentMonth - 1];
// Create the calendar header
console.log("Stage 1 achieved")
// Create the calendar body
const currentDate = today.getDate();
let row = document.createElement('tr');
calendarBody.appendChild(row);
for (let i = 0; i < firstDayOfMonth; i++) {
    const cell = document.createElement('td');
    cell.classList.add('day');
    cell.textContent = daysInPrevMonth - firstDayOfMonth + 1 + i;
    row.appendChild(cell);
    if (i % 7 === 6) {
        row = document.createElement('tr');
    }
}
console.log("Stage 2 achieved")
for (let i = firstDayOfMonth; i <= daysInMonth[currentMonth]; i++) {
    console.log(i)
    if (i % 7 === 0) {
        row = document.createElement('tr');
        calendarBody.appendChild(row);
    }
    const cell = document.createElement('td');
    cell.classList.add('day');
    cell.textContent = i;
    if (i === today.getDate() && currentMonth === today.getMonth() && currentYear === today.getFullYear()) {
        cell.classList.add('selected');
    }
    cell.addEventListener('click', () => {
        const selectedCells = document.querySelectorAll('.calendar .selected');
        selectedCells.forEach(cell => cell.classList.remove('selected'));
        cell.classList.add('selected');
    });
    row.appendChild(cell);
    
}
console.log("Stage 3 achieved")