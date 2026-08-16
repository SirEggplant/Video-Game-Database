const API_BASE = "http://localhost:8000";
const TOKEN_KEY = "gameshelf_token";
const PAGE_SIZE = 12;

const state = {
  token: localStorage.getItem(TOKEN_KEY),
  collections: [],
  allResults: [],          // full list of games for the current search
  currentPage: 0,
  totalResults: 0,
  currentParams: null,
  isLoading: false,
  isPreloading: false      // avoid duplicate background loads
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

const GENRES = [
  "Action", "Adventure", "RPG", "Strategy", "Simulation", "Sports",
  "Racing", "Fighting", "Shooter", "Puzzle", "Platformer", "Horror",
  "Survival", "Stealth", "Educational", "Music", "Party", "MMO",
  "FPS", "TPS", "Open World", "Sandbox", "Battle Royale", "Indie",
  "Casual", "Arcade", "Card Game", "Board Game", "Trivia"
];

// ---- Toast ----
function showToast(message, isError = false) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.className = `toast show${isError ? " error" : ""}`;
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => { toast.className = "toast"; }, 3400);
}

// ---- API wrapper ----
async function api(path, options = {}) {
  const headers = { ...(options.body ? { "Content-Type": "application/json" } : {}), ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new Error("Could not reach the API. Confirm it is running on port 8000.");
  }
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401 && state.token) logout("Your session has expired. Please sign in again.");
    throw new Error(payload.detail || "The request could not be completed.");
  }
  return payload;
}

// ---- App visibility ----
function showApp() {
  $("#login-view").classList.add("hidden");
  $("#app-view").classList.remove("hidden");
}

function logout(message) {
  localStorage.removeItem(TOKEN_KEY);
  state.token = null;
  $("#app-view").classList.add("hidden");
  $("#login-view").classList.remove("hidden");
  if (message) $("#login-error").textContent = message;
}

// ---- Helpers ----
function text(value, fallback = "—") { return value === null || value === undefined || value === "" ? fallback : value; }
function list(value) { return Array.isArray(value) ? value : []; }

function escapeHtml(value) {
  const node = document.createElement("span");
  node.textContent = value ?? "";
  return node.innerHTML;
}

// ---- Populate Genre Dropdown ----
function populateGenres() {
  const select = $("#search-genre");
  if (!select) return;
  select.innerHTML = '<option value="">All Genres</option>';
  GENRES.forEach(genre => {
    const option = document.createElement("option");
    option.value = genre;
    option.textContent = genre;
    select.appendChild(option);
  });
}

// ---- Game Card ----
function gameCard(game) {
  const card = document.createElement("article");
  card.className = "game-card";
  const tags = list(game.genres).slice(0, 2)
    .map((genre) => `<span class="tag">${escapeHtml(genre)}</span>`)
    .join("") || '<span class="tag">Uncategorized</span>';
  const platforms = list(game.platforms).join(" · ") || "Platform unavailable";
  card.innerHTML = `
    <div class="tag-row">${tags}</div>
    <h3>${escapeHtml(game.title)}</h3>
    <p class="game-meta">${escapeHtml(platforms)}</p>
    <p class="rating">★ ${text(game.total_user_rating, "No rating")}</p>
  `;
  return card;
}

// ---- Pagination ----
function renderPagination() {
  const container = $("#pagination-controls");
  if (!container) return;
  const totalPages = Math.ceil(state.totalResults / PAGE_SIZE) || 1;
  const current = state.currentPage;

  container.innerHTML = `
    <div class="pagination">
      <button class="button ghost" id="prev-page" ${current === 0 ? 'disabled' : ''}>← Previous</button>
      <span class="page-info">Page ${current + 1} of ${totalPages}</span>
      <button class="button ghost" id="next-page" ${current >= totalPages - 1 ? 'disabled' : ''}>Next →</button>
    </div>
  `;

  $("#prev-page")?.addEventListener("click", () => changePage(-1));
  $("#next-page")?.addEventListener("click", () => changePage(1));
}

function changePage(delta) {
  const totalPages = Math.ceil(state.totalResults / PAGE_SIZE);
  const newPage = state.currentPage + delta;
  if (newPage < 0 || newPage >= totalPages) return;
  state.currentPage = newPage;
  renderCurrentPage();
  renderPagination();
  // Scroll to top of results
  document.querySelector("#search-results")?.scrollIntoView({ behavior: "smooth" });
}

function renderCurrentPage() {
  const grid = $("#games-grid");
  if (!grid) return;
  const start = state.currentPage * PAGE_SIZE;
  const end = Math.min(start + PAGE_SIZE, state.allResults.length);
  const pageGames = state.allResults.slice(start, end);

  grid.replaceChildren();
  if (!pageGames.length) {
    grid.innerHTML = '<p class="empty-state">No games on this page.</p>';
    return;
  }
  pageGames.forEach(game => grid.append(gameCard(game)));
}

// ---- Preload remaining pages in background ----
async function preloadRemainingPages(params, total, loadedCount) {
  if (state.isPreloading) return;
  state.isPreloading = true;

  // Determine which offsets we still need
  const remainingOffsets = [];
  for (let offset = loadedCount; offset < total; offset += PAGE_SIZE) {
    remainingOffsets.push(offset);
  }

  // Fetch them sequentially (or in parallel with a limit)
  for (const offset of remainingOffsets) {
    try {
      const url = `/games/search?${params}&limit=${PAGE_SIZE}&offset=${offset}`;
      const response = await api(url);
      // Append to allResults
      state.allResults = state.allResults.concat(response.results);
      // Update total results (should be consistent, but keep)
      state.totalResults = response.total;
      // Optionally update UI if user is on a page that now has data (but we won't re-render)
    } catch (error) {
      console.warn("Failed to preload page", offset, error);
    }
  }

  state.isPreloading = false;
  // Re-render current page in case user is waiting (but we didn't change page)
  // However, if the user clicked to a page that wasn't loaded yet, it would have been empty.
  // Now that all pages are loaded, we could re-render, but we can just rely on changePage.
}

// ---- Search ----
async function searchGames(event) {
  event.preventDefault();
  if (state.isLoading) return;
  state.isLoading = true;

  const params = new URLSearchParams();
  const title = $("#search-title")?.value.trim();
  const genre = $("#search-genre")?.value;
  const platform = $("#search-platform")?.value.trim();
  const contributor = $("#search-contributor")?.value.trim();

  if (title) params.set("title", title);
  if (genre) params.set("genre", genre);
  if (platform) params.set("platform", platform);
  if (contributor) params.set("contributor", contributor);

  if (!params.size) {
    showToast("Enter a title, genre, platform, or contributor to search.", true);
    state.isLoading = false;
    return;
  }

  state.currentParams = params.toString();
  state.allResults = [];
  state.totalResults = 0;
  state.currentPage = 0;
  const grid = $("#games-grid");
  grid.innerHTML = '<p class="empty-state">Searching the catalog…</p>';

  try {
    // Fetch page 0 immediately
    const page0 = await api(`/games/search?${params}&limit=${PAGE_SIZE}&offset=0`);
    state.allResults = page0.results;
    state.totalResults = page0.total;
    state.currentPage = 0;
    renderCurrentPage();
    renderPagination();
    const countLabel = `${page0.total} game${page0.total === 1 ? "" : "s"} found (page 1)`;
    $("#result-count").textContent = countLabel;

    // Start preloading remaining pages in background
    preloadRemainingPages(state.currentParams, page0.total, PAGE_SIZE);
  } catch (error) {
    grid.innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
    state.allResults = [];
    state.totalResults = 0;
    renderPagination();
  } finally {
    state.isLoading = false;
  }
}

// ---- Collections ----
function renderCollections(collections) {
  const collectionList = $("#collections-list");
  const select = $("#collection-select");
  state.collections = collections;
  $("#collection-total").textContent = collections.length;
  collectionList.replaceChildren();
  select.replaceChildren(new Option("Choose a collection", ""));
  if (!collections.length) {
    collectionList.innerHTML = '<p class="empty-state">No collections yet. Create your first one.</p>';
  }
  collections.forEach((collection) => {
    const row = document.createElement("div");
    row.className = "collection-row";
    row.innerHTML = `
      <div>
        <strong>${escapeHtml(collection.collection_name)}</strong>
        <span>${collection.num_of_games} game${collection.num_of_games === 1 ? "" : "s"}</span>
      </div>
      <span>${collection.total_playtime || 0} min played</span>
    `;
    collectionList.append(row);
    select.add(new Option(collection.collection_name, collection.collection_name));
  });
}

async function loadCollections() {
  try {
    renderCollections(await api("/collections"));
  } catch (error) {
    $("#collections-list").innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
  }
}

async function createCollection(event) {
  event.preventDefault();
  const input = $("#new-collection-name");
  const collection_name = input.value.trim();
  if (!collection_name) return;
  try {
    await api("/collections", { method: "POST", body: JSON.stringify({ collection_name }) });
    input.value = "";
    await loadCollections();
    showToast("Collection created.");
  } catch (error) {
    showToast(error.message, true);
  }
}

// ---- Profile ----
async function loadProfile() {
  try {
    const [followers, following, recommendations] = await Promise.all([
      api("/social/followers"),
      api("/social/following"),
      api("/games/recommendations")
    ]);

    $("#profile-stats").innerHTML = [
      [state.collections.length, "Collections"],
      [followers.length, "Followers"],
      [following.length, "Following"]
    ].map(([value, label]) =>
      `<div class="stat"><strong>${value}</strong><span>${label}</span></div>`
    ).join("");

    const topGames = $("#top-games");
    topGames.replaceChildren();
    if (!recommendations.length) {
      topGames.innerHTML = '<li class="empty-state">No recommendations are available yet.</li>';
      return;
    }
    recommendations.slice(0, 10).forEach((game) => {
      const item = document.createElement("li");
      item.innerHTML = `
        <div>
          <strong>${escapeHtml(game.title)}</strong>
          <span>${escapeHtml(list(game.genres).slice(0, 2).join(" · ") || "Game")}</span>
        </div>
      `;
      topGames.append(item);
    });
  } catch (error) {
    $("#top-games").innerHTML = `<li class="empty-state">${escapeHtml(error.message)}</li>`;
  }
}

async function initializeDashboard() {
  showApp();
  await loadCollections();
  await loadProfile();
}

// ---- Event Listeners ----
document.addEventListener("DOMContentLoaded", () => {
  populateGenres();
  if (state.token) initializeDashboard();
});

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("#login-error").textContent = "";
  try {
    const response = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: $("#email").value.trim(),
        password: $("#password").value
      })
    });
    state.token = response.access_token;
    localStorage.setItem(TOKEN_KEY, state.token);
    await initializeDashboard();
  } catch (error) {
    $("#login-error").textContent = error.message;
  }
});

$("#search-form").addEventListener("submit", searchGames);
$("#create-collection-form").addEventListener("submit", createCollection);
$("#logout-button").addEventListener("click", () => logout());