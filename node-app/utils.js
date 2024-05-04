function isTimeBetween(startTimeStr, endTimeStr) {
    // Get current time
    const currentTime = new Date();

    // Extract hours and minutes from start time
    const [startHour, startMinute] = startTimeStr.split(':').map(Number);
    const startTime = new Date();
    startTime.setHours(startHour);
    startTime.setMinutes(startMinute);
    startTime.setSeconds(0); // Optional: set seconds to 0 if needed

    // Extract hours and minutes from end time
    const [endHour, endMinute] = endTimeStr.split(':').map(Number);
    const endTime = new Date();
    endTime.setHours(endHour);
    endTime.setMinutes(endMinute);
    endTime.setSeconds(0); // Optional: set seconds to 0 if needed

    // Check if current time is between start and end time
    return currentTime >= startTime && currentTime <= endTime;
}

module.exports = {
    isTimeBetween
};