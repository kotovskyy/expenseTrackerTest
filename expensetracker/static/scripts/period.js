function changePeriod(direction) {
    const monthNames = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];

    const currentPeriod = document.querySelector('.period').innerText.trim().split(' ');
    const currentMonth = currentPeriod[0];
    const currentYear = currentPeriod[1];

    const monthNumber = monthNames.indexOf(currentMonth) + 1;

    var newMonth = (direction === 'prev') ? monthNumber-1 : monthNumber+1;
    var newYear = parseInt(currentYear);
    
    if (newMonth > 12) {
        newMonth = 1;
        newYear = newYear + 1;
    }
    if (newMonth <= 0) {
        newMonth = 12;
        newYear = newYear - 1;
    }

    window.location.href = `/expensetracker/homepage/?month=${newMonth}&year=${newYear}`;
}