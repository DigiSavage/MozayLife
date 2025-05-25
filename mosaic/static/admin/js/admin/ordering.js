/**
 * reorder_init.js
 *
 * Handles drag-and-drop reordering for list items in a <ul id="orderthese">,
 * updating a hidden input field with the new order for form submission.
 * 
 * Modernized for clarity, maintainability, and standards compliance.
 * NOTE: Requires a working Drag library (not included here).
 */

window.addEventListener('DOMContentLoaded', reorder_init);

let lis;
const top = 0;
const left = 0;
const height = 30;

// Helper for backwards compatibility
function getBySelector(selector) {
    // Replace with standard querySelectorAll if possible
    if (document.querySelectorAll) {
        return document.querySelectorAll(selector);
    }
    // Otherwise fallback to custom method (not recommended)
    // Implement your own selector logic here if needed
    return [];
}

function reorder_init() {
    // Modern replacement for getElementsBySelector
    lis = getBySelector('ul#orderthese li');
    let input = getBySelector('input[name=order_]')[0];
    setOrder(input.value.split(','));
    input.disabled = true;
    draw();

    // Set up drag behavior for each li
    const limit = (lis.length - 1) * height;
    for (let i = 0; i < lis.length; i++) {
        let li = lis[i];
        let img = document.getElementById('handle' + li.id);
        li.style.zIndex = 1;
        // Requires a Drag library; otherwise this won't do anything
        if (typeof Drag !== "undefined") {
            Drag.init(img, li, left + 10, left + 10, top + 10, top + 10 + limit);
        }
        li.onDragStart = startDrag;
        li.onDragEnd = endDrag;
        img.style.cursor = 'move';
    }
}

function submitOrderForm() {
    let inputOrder = getBySelector('input[name=order_]')[0];
    inputOrder.value = getOrder();
    inputOrder.disabled = false;
}

function startDrag() {
    this.style.zIndex = '10';
    this.className = 'dragging';
}

function endDrag(x, y) {
    this.style.zIndex = '1';
    this.className = '';
    // Calculate new index based on y-coordinate
    let oldIndex = this.index;
    let newIndex = Math.round((y - 10 - top) / height);
    // Snap to correct position
    this.style.top = (10 + top + newIndex * height) + 'px';
    this.index = newIndex;
    moveItem(oldIndex, newIndex);
}

function moveItem(oldIndex, newIndex) {
    if (oldIndex === newIndex) return; // Nothing to swap

    let direction, lo, hi;
    if (newIndex > oldIndex) {
        lo = oldIndex;
        hi = newIndex;
        direction = -1;
    } else {
        direction = 1;
        hi = oldIndex;
        lo = newIndex;
    }
    let lis2 = new Array(lis.length);
    for (let i = 0; i < lis.length; i++) {
        if (i < lo || i > hi) {
            lis2[i] = lis[i];
        } else if (i === newIndex) {
            lis2[i] = lis[oldIndex];
        } else {
            lis2[i] = lis[i - direction];
        }
    }
    reIndex(lis2);
    lis = lis2;
    draw();
    getBySelector('input[name=order_]')[0].value = getOrder();
}

function reIndex(list) {
    for (let i = 0; i < list.length; i++) {
        list[i].index = i;
    }
}

function draw() {
    for (let i = 0; i < lis.length; i++) {
        let li = lis[i];
        li.index = i;
        li.style.position = 'absolute';
        li.style.left = (10 + left) + 'px';
        li.style.top = (10 + top + (i * height)) + 'px';
    }
}

function getOrder() {
    let order = new Array(lis.length);
    for (let i = 0; i < lis.length; i++) {
        // Remove the leading 'p' in the id (as per original)
        order[i] = lis[i].id.substring(1);
    }
    return order.join(',');
}

function setOrder(id_list) {
    let temp_lis = [];
    for (let i = 0; i < id_list.length; i++) {
        let id = 'p' + id_list[i];
        temp_lis.push(document.getElementById(id));
    }
    reIndex(temp_lis);
    lis = temp_lis;
    draw();
}

// Modern addEvent helper (use addEventListener in all new code)
function addEvent(elm, evType, fn, useCapture) {
    if (elm.addEventListener) {
        elm.addEventListener(evType, fn, useCapture);
        return true;
    } else if (elm.attachEvent) {
        return elm.attachEvent("on" + evType, fn);
    } else {
        elm['on' + evType] = fn;
    }
}