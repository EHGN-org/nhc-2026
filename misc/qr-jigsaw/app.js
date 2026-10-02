// TIP: You won't find a solution here in the code! You really have to solve this jigsaw puzzle by yourself
const BASE_SCALE = 20;
let SCALE = BASE_SCALE;

const table = document.getElementById("table");
const stage = document.getElementById("stage");
const board = document.getElementById("board");
const tray = document.getElementById("tray");
const toolbar = document.getElementById("toolbar");
const remainingEl = document.getElementById("remaining");
const controls = document.getElementById("controls");
const resetBtn = document.getElementById("reset");
const labelsToggle = document.getElementById("labels");
const statusEl = document.getElementById("status");
const liveEl = document.getElementById("live");

let boxSize = BOX_SIZE;
let colSizes = [];
let rowSizes = [];
let colOff = [];
let rowOff = [];
let z = 1;
let drag = null;
let applyingHash = false;
let dragRaf = 0;
let lastDragEvent = null;

const SCROLL_EDGE = 56;
const SCROLL_MAX = 18;

const occupied = new Map();
const slotEls = new Map();

function reduceMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function splitSizes(length, maxSize) {
  const sizes = [];
  for (let left = length; left > 0; left -= maxSize) sizes.push(Math.min(maxSize, left));
  return sizes;
}

function prefixes(sizes) {
  const out = [0];
  for (const size of sizes) out.push(out[out.length - 1] + size * SCALE);
  return out;
}

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load ${src}`));
    img.src = src;
  });
}

function boardOrigin() {
  const tableRect = table.getBoundingClientRect();
  const boardRect = board.getBoundingClientRect();
  return {
    x: boardRect.left - tableRect.left + table.scrollLeft + board.clientLeft,
    y: boardRect.top - tableRect.top + table.scrollTop + board.clientTop,
  };
}

function slotAt(col, row) {
  const { x, y } = boardOrigin();
  return {
    x: x + colOff[col],
    y: y + rowOff[row],
    w: colSizes[col] * SCALE,
    h: rowSizes[row] * SCALE,
    col,
    row,
  };
}

function cellOf(el) {
  for (const [cell, piece] of occupied) {
    if (piece === el) return cell;
  }
  return null;
}

function release(el) {
  const cell = cellOf(el);
  if (cell !== null) occupied.delete(cell);
  el.classList.remove("placed", "settling");
}

function nearestSlot(el, x, y) {
  const cx = x + el.offsetWidth / 2;
  const cy = y + el.offsetHeight / 2;
  for (let row = 0; row < rowSizes.length; row++) {
    for (let col = 0; col < colSizes.length; col++) {
      const key = `${col},${row}`;
      if (occupied.has(key)) continue;
      const slot = slotAt(col, row);
      if (slot.w !== el.offsetWidth || slot.h !== el.offsetHeight) continue;
      if (cx >= slot.x && cx <= slot.x + slot.w && cy >= slot.y && cy <= slot.y + slot.h) {
        return slot;
      }
    }
  }
  return null;
}

function place(el, x, y) {
  el.style.left = `${x}px`;
  el.style.top = `${y}px`;
}

function pointerOnTable(event, dx, dy) {
  const tableRect = table.getBoundingClientRect();
  return {
    x: event.clientX - tableRect.left + table.scrollLeft - dx,
    y: event.clientY - tableRect.top + table.scrollTop - dy,
  };
}

function contentExtent() {
  const page = table.querySelector(".page");
  return page ? page.offsetHeight : Math.max(stage.offsetTop + stage.offsetHeight, tray.offsetTop + tray.offsetHeight);
}

function hostScrollMax(host) {
  if (host === table) return Math.max(0, contentExtent() - table.clientHeight);
  return Math.max(0, host.scrollHeight - host.clientHeight);
}

function clampToTable(el, x, y) {
  const maxX = Math.max(0, table.scrollLeft + table.clientWidth - el.offsetWidth);
  const maxY = Math.max(
    0,
    Math.min(table.scrollTop + table.clientHeight, contentExtent()) - el.offsetHeight,
  );
  return {
    x: Math.min(maxX, Math.max(table.scrollLeft, x)),
    y: Math.min(maxY, Math.max(table.scrollTop, y)),
  };
}

function boardOffset() {
  const narrow = table.clientWidth < 700;
  return {
    left: narrow ? 16 : 40,
    top: narrow ? 12 : 24,
    right: narrow ? 16 : 40,
  };
}

function fitScale() {
  const { left, right } = boardOffset();
  const style = getComputedStyle(board);
  const borderX = (parseFloat(style.borderLeftWidth) || 0) + (parseFloat(style.borderRightWidth) || 0);
  const cells = FULL_WIDTH / BOX_SIZE;
  const avail = table.clientWidth - left - right - borderX;
  return Math.max(6, Math.min(BASE_SCALE, Math.floor(avail / cells)));
}

function sizePiece(el) {
  const img = el.querySelector("img");
  if (!img?.naturalWidth) return;
  el.style.width = `${(img.naturalWidth / boxSize) * SCALE}px`;
  el.style.height = `${(img.naturalHeight / boxSize) * SCALE}px`;
}

function applyBoardMetrics() {
  const { left, top } = boardOffset();
  SCALE = fitScale();
  colOff = prefixes(colSizes);
  rowOff = prefixes(rowSizes);
  board.style.gridTemplateColumns = colSizes.map((size) => `${size * SCALE}px`).join(" ");
  board.style.gridTemplateRows = rowSizes.map((size) => `${size * SCALE}px`).join(" ");
  board.style.left = `${left}px`;
  board.style.top = `${top}px`;
  for (const el of table.querySelectorAll(".piece")) sizePiece(el);
}

function layoutPlaced() {
  for (const [key, el] of occupied) {
    const [col, row] = key.split(",").map(Number);
    place(el, slotAt(col, row).x, slotAt(col, row).y);
  }
}

function useSideTray() {
  const pieceW = (colSizes[0] || 5) * SCALE;
  const stageW = board.offsetLeft + board.offsetWidth + 16;
  const trayInner = table.clientWidth - stageW - 48;
  return trayInner >= pieceW * 2 + 12 + 16;
}

function layoutShell() {
  applyBoardMetrics();
  table.classList.toggle("tray-side", useSideTray());
  stage.style.width = useSideTray() ? `${board.offsetLeft + board.offsetWidth + 16}px` : "100%";
  stage.style.minHeight = `${board.offsetTop + board.offsetHeight + toolbar.offsetHeight + 28}px`;
  positionReset();
  layoutPlaced();
}

function dockToTable(el) {
  el.classList.remove("in-tray");
  table.append(el);
}

function dockToTray(el) {
  el.classList.remove("placed", "settling", "dragging");
  el.classList.add("in-tray");
  el.style.left = "";
  el.style.top = "";
  tray.append(el);
}

function setHotSlot(slot) {
  for (const cell of slotEls.values()) cell.classList.remove("is-hot");
  if (!slot) return;
  slotEls.get(`${slot.col},${slot.row}`)?.classList.add("is-hot");
}

function pieceNum(el) {
  return el.dataset.n;
}

function announce(message) {
  liveEl.textContent = "";
  liveEl.textContent = message;
}

// Board hash: base64url of (piece, slot) pairs. Padding bits are 1s so they cannot form a pair.
const B64URL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";

function bitWidth(n) {
  return n <= 1 ? 1 : Math.ceil(Math.log2(n));
}

function slotCount() {
  return colSizes.length * rowSizes.length;
}

function slotIndex(col, row) {
  return row * colSizes.length + col;
}

function slotCoords(slot) {
  const cols = colSizes.length;
  return { col: slot % cols, row: Math.floor(slot / cols) };
}

function hashWidths() {
  const slots = slotCount();
  return {
    slots,
    pieceBits: bitWidth(PIECE_COUNT),
    slotBits: bitWidth(slots),
  };
}

function encodeBits(fields) {
  const bits = [];
  for (const [value, width] of fields) {
    for (let i = width - 1; i >= 0; i--) bits.push((value >> i) & 1);
  }
  while (bits.length % 6) bits.push(1);
  let out = "";
  for (let i = 0; i < bits.length; i += 6) {
    let n = 0;
    for (let j = 0; j < 6; j++) n = (n << 1) | bits[i + j];
    out += B64URL[n];
  }
  return out;
}

function decodeBits(raw) {
  const bits = [];
  for (const ch of raw) {
    const n = B64URL.indexOf(ch);
    if (n < 0) return null;
    for (let i = 5; i >= 0; i--) bits.push((n >> i) & 1);
  }
  let pos = 0;
  return {
    read(width) {
      if (pos + width > bits.length) return null;
      let n = 0;
      for (let i = 0; i < width; i++) n = (n << 1) | bits[pos++];
      return n;
    },
    remain() {
      return bits.length - pos;
    },
  };
}

function updateRemaining() {
  const n = Math.max(0, PIECE_COUNT - occupied.size);
  remainingEl.textContent = n === 1 ? "1 piece left" : `${n} pieces left`;
}

function writeHash() {
  updateRemaining();
  if (applyingHash) return;
  const { slots: nSlots, pieceBits, slotBits } = hashWidths();
  const fields = [...occupied.entries()]
    .map(([key, el]) => {
      const n = Number(pieceNum(el));
      const [col, row] = key.split(",").map(Number);
      return { n, slot: slotIndex(col, row) };
    })
    .filter((rec) => rec.n >= 1 && rec.n <= PIECE_COUNT && rec.slot >= 0 && rec.slot < nSlots)
    .sort((a, b) => a.n - b.n)
    .flatMap((rec) => [[rec.n - 1, pieceBits], [rec.slot, slotBits]]);
  const payload = fields.length ? encodeBits(fields) : "";
  const next = payload ? `#${payload}` : "";
  const url = `${location.pathname}${location.search}${next}`;
  if (`${location.pathname}${location.search}${location.hash}` !== url) {
    history.replaceState(null, "", url);
  }
}

function readHash() {
  const raw = location.hash.replace(/^#/, "");
  if (!raw) return [];
  const reader = decodeBits(raw);
  if (!reader) return [];
  const { slots: nSlots, pieceBits, slotBits } = hashWidths();
  const out = [];
  const used = new Set();
  const pairBits = pieceBits + slotBits;
  while (reader.remain() >= pairBits) {
    const piece = reader.read(pieceBits);
    const loc = reader.read(slotBits);
    if (piece === null || loc === null || piece >= PIECE_COUNT || loc >= nSlots) break;
    if (used.has(loc)) continue;
    used.add(loc);
    out.push({ id: String(piece + 1), ...slotCoords(loc) });
  }
  return out;
}

function applyHash() {
  applyingHash = true;
  scatterPieces();
  const byId = new Map([...table.querySelectorAll(".piece")].map((el) => [pieceNum(el), el]));
  for (const rec of readHash()) {
    const el = byId.get(rec.id);
    if (!el) continue;
    if (rec.col < 0 || rec.row < 0 || rec.col >= colSizes.length || rec.row >= rowSizes.length) continue;
    const key = `${rec.col},${rec.row}`;
    if (occupied.has(key)) continue;
    const slot = slotAt(rec.col, rec.row);
    if (slot.w !== el.offsetWidth || slot.h !== el.offsetHeight) continue;
    release(el);
    dockToTable(el);
    place(el, slot.x, slot.y);
    occupied.set(key, el);
    el.classList.add("placed");
  }
  applyingHash = false;
  writeHash();
}

function positionReset() {
  toolbar.style.left = `${board.offsetLeft}px`;
  toolbar.style.top = `${board.offsetTop + board.offsetHeight + 14}px`;
  toolbar.style.width = `${board.offsetWidth}px`;
}

function scrollHost() {
  if (table.classList.contains("tray-side") && hostScrollMax(tray) > 1) return tray;
  if (hostScrollMax(table) > 1) return table;
  return null;
}

function autoScrollFromPointer(event) {
  const host = scrollHost();
  if (!host) return;
  const max = hostScrollMax(host);
  if (max <= 0) return;
  const rect = table.getBoundingClientRect();
  const y = event.clientY;
  let delta = 0;
  if (y < rect.top + SCROLL_EDGE && host.scrollTop > 0) {
    const t = 1 - Math.max(0, y - rect.top) / SCROLL_EDGE;
    delta = -Math.ceil(SCROLL_MAX * t * t);
  } else if (y > rect.bottom - SCROLL_EDGE && host.scrollTop < max) {
    const t = 1 - Math.max(0, rect.bottom - y) / SCROLL_EDGE;
    delta = Math.ceil(SCROLL_MAX * t * t);
  }
  if (!delta) return;
  host.scrollTop = Math.min(max, Math.max(0, host.scrollTop + delta));
}

function followPointer(event) {
  const point = pointerOnTable(event, drag.dx, drag.dy);
  const next = clampToTable(drag.el, point.x, point.y);
  place(drag.el, next.x, next.y);
  setHotSlot(nearestSlot(drag.el, next.x, next.y));
}

function dragTick() {
  dragRaf = 0;
  if (!drag || !lastDragEvent) return;
  autoScrollFromPointer(lastDragEvent);
  followPointer(lastDragEvent);
  dragRaf = requestAnimationFrame(dragTick);
}

function startDragTick() {
  if (!dragRaf) dragRaf = requestAnimationFrame(dragTick);
}

function stopDragTick() {
  if (dragRaf) cancelAnimationFrame(dragRaf);
  dragRaf = 0;
  lastDragEvent = null;
}

function stopDragListeners() {
  stopDragTick();
  window.removeEventListener("pointermove", onDragMove);
  window.removeEventListener("pointerup", onDragEnd);
  window.removeEventListener("pointercancel", onDragEnd);
}

function resetPuzzle() {
  if (!confirm("Reset the puzzle? All placed pieces will return to the tray.")) return;
  if (drag) {
    stopDragListeners();
    drag.el.classList.remove("dragging");
    setHotSlot(null);
    drag = null;
  }
  scatterPieces();
  writeHash();
  announce("Puzzle reset.");
}

function scatterPieces() {
  occupied.clear();
  const pieces = [...table.querySelectorAll(".piece")].sort(
    (a, b) => Number(a.dataset.n) - Number(b.dataset.n),
  );
  for (const el of pieces) dockToTray(el);
  layoutShell();
}

function endDrag(el) {
  if (!drag || drag.el !== el) return;
  stopDragListeners();
  const next = clampToTable(el, parseFloat(el.style.left), parseFloat(el.style.top));
  const slot = nearestSlot(el, next.x, next.y);
  const key = slot ? `${slot.col},${slot.row}` : null;
  if (slot && !occupied.has(key)) {
    place(el, slot.x, slot.y);
    occupied.set(key, el);
    el.classList.add("placed");
    if (!reduceMotion()) {
      el.classList.remove("settling");
      void el.offsetWidth;
      el.classList.add("settling");
    }
    announce("Piece placed on the board.");
  } else {
    dockToTray(el);
  }
  el.classList.remove("dragging");
  setHotSlot(null);
  drag = null;
  writeHash();
}

function onDragMove(event) {
  if (!drag || event.pointerId !== drag.pointerId) return;
  lastDragEvent = event;
  followPointer(event);
}

function onDragEnd(event) {
  if (!drag || event.pointerId !== drag.pointerId) return;
  endDrag(drag.el);
}

function bindPiece(el) {
  el.addEventListener("pointerdown", (event) => {
    if (event.button !== 0 || drag) return;
    event.preventDefault();
    const rect = el.getBoundingClientRect();
    drag = {
      el,
      pointerId: event.pointerId,
      dx: event.clientX - rect.left,
      dy: event.clientY - rect.top,
    };
    release(el);
    dockToTable(el);
    writeHash();
    el.classList.add("dragging");
    el.style.zIndex = String(++z);
    const point = pointerOnTable(event, drag.dx, drag.dy);
    const next = clampToTable(el, point.x, point.y);
    place(el, next.x, next.y);
    setHotSlot(nearestSlot(el, next.x, next.y));
    try {
      el.setPointerCapture(event.pointerId);
    } catch {
      /* capture is optional; window listeners keep the drag alive */
    }
    lastDragEvent = event;
    startDragTick();
    window.addEventListener("pointermove", onDragMove);
    window.addEventListener("pointerup", onDragEnd);
    window.addEventListener("pointercancel", onDragEnd);
  });

  el.addEventListener("animationend", (event) => {
    if (event.animationName === "settle") el.classList.remove("settling");
  });
}

function setupBoard() {
  boxSize = BOX_SIZE;
  const colsGuess = Math.max(1, Math.round(Math.sqrt(PIECE_COUNT * (FULL_WIDTH / FULL_HEIGHT))));
  const maxPiecePx = Math.max(BOX_SIZE, Math.round(FULL_WIDTH / colsGuess));
  colSizes = splitSizes(FULL_WIDTH, maxPiecePx).map((px) => px / boxSize);
  rowSizes = splitSizes(FULL_HEIGHT, maxPiecePx).map((px) => px / boxSize);
  colOff = prefixes(colSizes);
  rowOff = prefixes(rowSizes);

  applyBoardMetrics();

  for (let row = 0; row < rowSizes.length; row++) {
    for (let col = 0; col < colSizes.length; col++) {
      const cell = document.createElement("div");
      cell.className = "slot";
      cell.dataset.col = String(col);
      cell.dataset.row = String(row);
      cell.setAttribute("role", "gridcell");
      slotEls.set(`${col},${row}`, cell);
      board.append(cell);
    }
  }
}

function tryPlaceRecord(el, rec) {
  if (rec.col < 0 || rec.row < 0 || rec.col >= colSizes.length || rec.row >= rowSizes.length) return false;
  const key = `${rec.col},${rec.row}`;
  if (occupied.has(key)) return false;
  const slot = slotAt(rec.col, rec.row);
  if (slot.w !== el.offsetWidth || slot.h !== el.offsetHeight) return false;
  dockToTable(el);
  place(el, slot.x, slot.y);
  occupied.set(key, el);
  el.classList.add("placed");
  updateRemaining();
  return true;
}

function addPiece(img, n, saved) {
  const w = (img.naturalWidth / boxSize) * SCALE;
  const h = (img.naturalHeight / boxSize) * SCALE;
  const el = document.createElement("div");
  el.className = "piece";
  el.dataset.id = `${n}.png`;
  el.dataset.n = String(n);
  el.style.width = `${w}px`;
  el.style.height = `${h}px`;
  el.tabIndex = 0;
  el.setAttribute("role", "button");
  el.setAttribute("aria-label", `Puzzle piece ${n}`);
  const picture = document.createElement("img");
  picture.src = img.src;
  picture.alt = "";
  picture.draggable = false;
  el.append(picture);
  el.style.order = String(n);
  bindPiece(el);
  dockToTray(el);

  const rec = saved.get(String(n));
  if (rec) tryPlaceRecord(el, rec);
  layoutShell();
}

async function main() {
  console.log("TIP: You won't find a solution here in the code! You really have to solve this jigsaw puzzle by yourself");
  setupBoard();
  layoutShell();
  updateRemaining();
  resetBtn.addEventListener("click", resetPuzzle);
  labelsToggle.addEventListener("change", () => {
    table.classList.toggle("show-labels", labelsToggle.checked);
  });

  const saved = new Map(readHash().map((rec) => [rec.id, rec]));
  const results = await Promise.allSettled(
    Array.from({ length: PIECE_COUNT }, (_, i) =>
      loadImage(`pieces/${i + 1}.png`).then((img) => addPiece(img, i + 1, saved)),
    ),
  );

  const loaded = results.filter((result) => result.status === "fulfilled").length;
  if (!loaded) throw new Error("Failed to load puzzle pieces");
  writeHash();
}

window.addEventListener("hashchange", () => {
  if (!colSizes.length || applyingHash) return;
  applyHash();
});

window.addEventListener("resize", () => {
  if (!colSizes.length) return;
  layoutShell();
});

main().catch((err) => {
  console.error(err);
  statusEl.hidden = false;
  statusEl.textContent = "Could not load the puzzle pieces. Refresh to try again.";
});
