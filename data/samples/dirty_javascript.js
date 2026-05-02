/**
 * Sample inefficient JavaScript code with carbon-heavy patterns.
 * This file is intentionally written poorly for testing GreenCode Sentinel.
 */

/**
 * ISSUE: Nested loops with O(n³) complexity
 */
function inefficientDataProcessing(dataArray) {
    const results = [];
    
    // ISSUE: Triple nested loop
    for (let i = 0; i < dataArray.length; i++) {
        for (let j = 0; j < dataArray.length; j++) {
            for (let k = 0; k < dataArray.length; k++) {
                if (dataArray[i] + dataArray[j] === dataArray[k]) {
                    results.push([dataArray[i], dataArray[j], dataArray[k]]);
                }
            }
        }
    }
    
    return results;
}

/**
 * ISSUE: Redundant API calls without caching
 */
async function redundantApiCalls(userIds) {
    const userData = [];
    
    // ISSUE: Sequential API calls instead of Promise.all
    for (const userId of userIds) {
        // ISSUE: Multiple calls for same resource
        const response1 = await fetch(`https://api.example.com/users/${userId}`);
        const user = await response1.json();
        
        const response2 = await fetch(`https://api.example.com/users/${userId}/profile`);
        const profile = await response2.json();
        
        userData.push({ user, profile });
    }
    
    return userData;
}

/**
 * ISSUE: Memory leaks from event listeners
 */
function memoryLeakExample() {
    const elements = document.querySelectorAll('.item');
    
    // ISSUE: Event listeners not removed, causing memory leaks
    elements.forEach(element => {
        element.addEventListener('click', function() {
            console.log('Clicked:', element.id);
            // ISSUE: Closure captures entire element
            const data = element.dataset;
            processData(data);
        });
    });
    
    // ISSUE: Creating new intervals without clearing old ones
    setInterval(() => {
        console.log('Running...');
    }, 1000);
}

/**
 * ISSUE: Inefficient DOM manipulation
 */
function inefficientDomManipulation(items) {
    const container = document.getElementById('container');
    
    // ISSUE: Manipulating DOM in loop causes multiple reflows
    items.forEach(item => {
        const div = document.createElement('div');
        div.textContent = item;
        container.appendChild(div);  // ISSUE: Triggers reflow each time
    });
    
    // ISSUE: Reading layout properties in loop
    items.forEach(item => {
        const element = document.getElementById(item);
        const height = element.offsetHeight;  // ISSUE: Forces layout recalculation
        element.style.height = (height + 10) + 'px';
    });
}

/**
 * ISSUE: Inefficient array operations
 */
function inefficientArrayOperations(data) {
    let result = [];
    
    // ISSUE: Using array methods inefficiently
    data.forEach(item => {
        result.push(item * 2);
    });
    
    // ISSUE: Chaining multiple array iterations
    result = result
        .map(x => x + 1)
        .filter(x => x > 0)
        .map(x => x * 2)
        .filter(x => x < 1000);
    
    // ISSUE: Using indexOf in loop - O(n²)
    const unique = [];
    data.forEach(item => {
        if (unique.indexOf(item) === -1) {  // Should use Set
            unique.push(item);
        }
    });
    
    return { result, unique };
}

/**
 * ISSUE: Blocking synchronous operations
 */
function blockingOperations(largeArray) {
    // ISSUE: Synchronous heavy computation blocks UI
    const result = largeArray.map(item => {
        let sum = 0;
        for (let i = 0; i < 10000; i++) {
            sum += Math.sqrt(item * i);
        }
        return sum;
    });
    
    return result;
}

/**
 * ISSUE: Inefficient string concatenation
 */
function inefficientStringBuilding(items) {
    let result = '';
    
    // ISSUE: String concatenation in loop
    for (const item of items) {
        result = result + item + ',';  // Should use array.join()
    }
    
    return result;
}

/**
 * ISSUE: Memory inefficient data structures
 */
function memoryInefficient(size) {
    // ISSUE: Creating large unnecessary arrays
    const array1 = new Array(size).fill(0);
    const array2 = new Array(size).fill(0);
    const array3 = new Array(size).fill(0);
    
    // ISSUE: Copying entire arrays when not needed
    const copy1 = [...array1];
    const copy2 = [...array2];
    const copy3 = [...array3];
    
    return { array1, array2, array3, copy1, copy2, copy3 };
}

// Helper function
function processData(data) {
    console.log('Processing:', data);
}

// Run inefficient operations
console.log('Running inefficient JavaScript operations...');
const testData = Array.from({ length: 50 }, (_, i) => i);
const result1 = inefficientDataProcessing(testData.slice(0, 10));
const result2 = inefficientArrayOperations(testData);
console.log('Done! (But consumed excessive energy)');

// Made with Bob
