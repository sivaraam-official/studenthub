/**
 * StudentHub Application Logic.
 * Manages state, UI rendering, event listeners, modals, and backend synchronization.
 */

// Global State
const state = {
  students: [],
  total: 0,
  page: 1,
  limit: 10,
  totalPages: 1,
  search: "",
  course: "all",
  sortBy: "id",
  order: "desc",
  selectedStudent: null,
  deleteTargetId: null,
  loading: false,
};

// DOM Elements Cache
const DOM = {
  // Sidebar & Layout
  sidebar: document.getElementById("sidebar"),
  sidebarBackdrop: document.getElementById("sidebar-backdrop"),
  menuToggle: document.getElementById("menu-toggle"),
  backendStatusText: document.getElementById("backend-status-text"),
  
  // Header Actions
  refreshBtn: document.getElementById("refresh-btn"),
  openAddModalBtn: document.getElementById("open-add-modal-btn"),
  
  // Stats
  statTotalStudents: document.getElementById("stat-total-students"),
  statTotalCourses: document.getElementById("stat-total-courses"),
  
  // Filters & Search
  searchInput: document.getElementById("search-input"),
  courseFilter: document.getElementById("course-filter"),
  sortBy: document.getElementById("sort-by"),
  sortOrder: document.getElementById("sort-order"),
  clearFiltersBtn: document.getElementById("clear-filters-btn"),
  
  // Table
  tableBody: document.getElementById("students-table-body"),
  emptyState: document.getElementById("empty-state"),
  emptyAddBtn: document.getElementById("empty-add-btn"),
  paginationInfo: document.getElementById("pagination-info"),
  paginationControls: document.getElementById("pagination-controls"),
  
  // Add Modal
  addModal: document.getElementById("add-modal"),
  addForm: document.getElementById("add-student-form"),
  closeAddModal: document.getElementById("close-add-modal"),
  cancelAddBtn: document.getElementById("cancel-add-btn"),
  submitAddBtn: document.getElementById("submit-add-btn"),
  
  // Edit Modal
  editModal: document.getElementById("edit-modal"),
  editForm: document.getElementById("edit-student-form"),
  closeEditModal: document.getElementById("close-edit-modal"),
  cancelEditBtn: document.getElementById("cancel-edit-btn"),
  submitEditBtn: document.getElementById("submit-edit-btn"),
  
  // View Modal
  viewModal: document.getElementById("view-modal"),
  viewModalBody: document.getElementById("view-modal-body"),
  closeViewModal: document.getElementById("close-view-modal"),
  closeViewBtn: document.getElementById("close-view-btn"),
  viewEditShortcutBtn: document.getElementById("view-edit-shortcut-btn"),
  
  // Delete Modal
  deleteModal: document.getElementById("delete-modal"),
  deleteStudentName: document.getElementById("delete-student-name"),
  deleteStudentId: document.getElementById("delete-student-id"),
  closeDeleteModal: document.getElementById("close-delete-modal"),
  cancelDeleteBtn: document.getElementById("cancel-delete-btn"),
  confirmDeleteBtn: document.getElementById("confirm-delete-btn"),
  
  // Toast
  toastContainer: document.getElementById("toast-container"),
};

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

/**
 * Display a user-friendly toast message.
 */
function showToast(title, message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  const iconSvg = type === "success"
    ? `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>`
    : type === "error"
    ? `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>`
    : `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`;

  toast.innerHTML = `
    <div class="toast-icon">${iconSvg}</div>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-message">${message}</div>
    </div>
    <button class="toast-close" aria-label="Close notification">✕</button>
  `;

  DOM.toastContainer.appendChild(toast);

  const closeBtn = toast.querySelector(".toast-close");
  const removeToast = () => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    setTimeout(() => toast.remove(), 250);
  };

  closeBtn.addEventListener("click", removeToast);
  setTimeout(removeToast, 4500);
}

/**
 * Get student initials for avatar icon.
 */
function getInitials(name) {
  if (!name) return "ST";
  const parts = name.trim().split(" ");
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/**
 * Format date string into readable format.
 */
function formatDate(dateStr) {
  if (!dateStr) return "N/A";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
  } catch {
    return dateStr;
  }
}

/**
 * Format timestamp into date & time.
 */
function formatTimestamp(timestampStr) {
  if (!timestampStr) return "N/A";
  try {
    const d = new Date(timestampStr);
    if (isNaN(d.getTime())) return timestampStr;
    return d.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return timestampStr;
  }
}

/**
 * Set button into loading spinner state.
 */
function setButtonLoading(button, isLoading, normalText = "Submit") {
  if (isLoading) {
    button.disabled = true;
    button.dataset.originalHtml = button.innerHTML;
    button.innerHTML = `<span class="spinner"></span> <span>Processing...</span>`;
  } else {
    button.disabled = false;
    button.innerHTML = button.dataset.originalHtml || `<span>${normalText}</span>`;
  }
}

// ==========================================
// MODAL CONTROLS
// ==========================================

function openModal(modal) {
  modal.classList.add("show");
  document.body.style.overflow = "hidden";
}

function closeModal(modal) {
  modal.classList.remove("show");
  document.body.style.overflow = "";
}

// Close modals when clicking backdrop
document.querySelectorAll(".modal-backdrop").forEach(backdrop => {
  backdrop.addEventListener("click", (e) => {
    if (e.target === backdrop) {
      closeModal(backdrop);
    }
  });
});

// Escape key closes open modals
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    document.querySelectorAll(".modal-backdrop.show").forEach(closeModal);
    if (DOM.sidebar.classList.contains("open")) {
      DOM.sidebar.classList.remove("open");
      DOM.sidebarBackdrop.classList.remove("show");
    }
  }
});

// ==========================================
// DATA FETCHING & RENDERING
// ==========================================

/**
 * Fetch and update dashboard metrics.
 */
async function loadStats() {
  try {
    const stats = await window.ApiService.getStats();
    DOM.statTotalStudents.textContent = stats.total_students ?? 0;
    DOM.statTotalCourses.textContent = stats.total_courses ?? 0;

    // Dynamically update course filter options
    const currentSelected = DOM.courseFilter.value;
    const courses = Object.keys(stats.course_counts || {}).sort();

    DOM.courseFilter.innerHTML = `<option value="all">All Courses</option>`;
    courses.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c;
      opt.textContent = `${c} (${stats.course_counts[c]})`;
      if (c === currentSelected) opt.selected = true;
      DOM.courseFilter.appendChild(opt);
    });
  } catch (err) {
    console.error("Failed to load statistics:", err);
  }
}

/**
 * Fetch students list from backend and render table.
 */
async function loadStudents() {
  if (state.loading) return;
  state.loading = true;

  // Render loading skeleton
  DOM.tableBody.innerHTML = `
    <tr>
      <td colspan="7" style="text-align: center; padding: 3rem;">
        <span class="spinner spinner-dark" style="width: 28px; height: 28px;"></span>
        <div style="margin-top: 0.75rem; color: var(--text-muted); font-size: 0.9rem;">Fetching student records from database...</div>
      </td>
    </tr>
  `;
  DOM.emptyState.style.display = "none";

  try {
    const res = await window.ApiService.getStudents({
      page: state.page,
      limit: state.limit,
      search: state.search,
      course: state.course,
      sort_by: state.sortBy,
      order: state.order,
    });

    state.students = res.students || [];
    state.total = res.total || 0;
    state.page = res.page || 1;
    state.totalPages = res.total_pages || 1;

    renderTable();
    renderPagination();
  } catch (err) {
    DOM.tableBody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; padding: 3rem; color: var(--danger);">
          <strong>Failed to load student records:</strong> ${err.message}
          <div style="margin-top: 1rem;">
            <button class="btn btn-secondary" onclick="loadStudents()">Try Again</button>
          </div>
        </td>
      </tr>
    `;
    showToast("Error Loading Data", err.message, "error");
  } finally {
    state.loading = false;
  }
}

/**
 * Render student records into the HTML table.
 */
function renderTable() {
  DOM.tableBody.innerHTML = "";

  if (state.students.length === 0) {
    DOM.emptyState.style.display = "flex";
    return;
  }

  DOM.emptyState.style.display = "none";

  state.students.forEach(student => {
    const tr = document.createElement("tr");

    const initials = getInitials(student.name);
    const dobFormatted = formatDate(student.date_of_birth);
    const enrollmentFormatted = formatDate(student.enrollment_date);
    const courseBadge = student.course
      ? `<span class="badge badge-course">${student.course}</span>`
      : `<span style="color: var(--text-light); font-size: 0.8rem;">Unassigned</span>`;
    const phoneDisplay = student.phone
      ? `<span class="phone-text">${student.phone}</span>`
      : "";

    tr.innerHTML = `
      <td style="font-weight: 600; color: var(--text-muted);">#${student.id}</td>
      <td>
        <div class="student-cell">
          <div class="avatar-badge">${initials}</div>
          <div class="student-meta">
            <span class="student-name">${student.name}</span>
            <span class="student-id">Student ID: #${student.id}</span>
          </div>
        </div>
      </td>
      <td>${dobFormatted}</td>
      <td>
        <div class="contact-meta">
          <a href="mailto:${student.email}" class="email-link">${student.email}</a>
          ${phoneDisplay}
        </div>
      </td>
      <td>${courseBadge}</td>
      <td>${enrollmentFormatted}</td>
      <td style="text-align: right;">
        <div class="action-buttons" style="justify-content: flex-end;">
          <button class="icon-btn view-btn" data-id="${student.id}" title="View Details">
            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
            </svg>
          </button>
          <button class="icon-btn edit-btn" data-id="${student.id}" title="Edit Student">
            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
            </svg>
          </button>
          <button class="icon-btn delete-btn" data-id="${student.id}" data-name="${student.name}" title="Delete Record">
            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </td>
    `;

    DOM.tableBody.appendChild(tr);
  });

  // Attach event listeners to action buttons
  DOM.tableBody.querySelectorAll(".view-btn").forEach(btn => {
    btn.addEventListener("click", () => handleViewStudent(Number(btn.dataset.id)));
  });

  DOM.tableBody.querySelectorAll(".edit-btn").forEach(btn => {
    btn.addEventListener("click", () => handleEditStudent(Number(btn.dataset.id)));
  });

  DOM.tableBody.querySelectorAll(".delete-btn").forEach(btn => {
    btn.addEventListener("click", () => handleDeletePrompt(Number(btn.dataset.id), btn.dataset.name));
  });
}

/**
 * Render pagination numbers and entry counts.
 */
function renderPagination() {
  if (state.total === 0) {
    DOM.paginationInfo.textContent = "Showing 0 to 0 of 0 entries";
    DOM.paginationControls.innerHTML = "";
    return;
  }

  const startEntry = (state.page - 1) * state.limit + 1;
  const endEntry = Math.min(state.page * state.limit, state.total);
  DOM.paginationInfo.textContent = `Showing ${startEntry} to ${endEntry} of ${state.total} entries`;

  DOM.paginationControls.innerHTML = "";

  // Previous Button
  const prevBtn = document.createElement("button");
  prevBtn.className = "page-btn";
  prevBtn.innerHTML = "&laquo;";
  prevBtn.disabled = state.page <= 1;
  prevBtn.title = "Previous page";
  prevBtn.addEventListener("click", () => {
    if (state.page > 1) {
      state.page--;
      loadStudents();
    }
  });
  DOM.paginationControls.appendChild(prevBtn);

  // Page Numbers
  for (let i = 1; i <= state.totalPages; i++) {
    // Show first, last, current, and neighbours
    if (i === 1 || i === state.totalPages || (i >= state.page - 1 && i <= state.page + 1)) {
      const pageBtn = document.createElement("button");
      pageBtn.className = `page-btn ${i === state.page ? "active" : ""}`;
      pageBtn.textContent = i;
      pageBtn.addEventListener("click", () => {
        if (state.page !== i) {
          state.page = i;
          loadStudents();
        }
      });
      DOM.paginationControls.appendChild(pageBtn);
    } else if (
      (i === state.page - 2 && state.page > 3) ||
      (i === state.page + 2 && state.page < state.totalPages - 2)
    ) {
      const ellipsis = document.createElement("span");
      ellipsis.textContent = "...";
      ellipsis.style.padding = "0 0.35rem";
      ellipsis.style.color = "var(--text-light)";
      DOM.paginationControls.appendChild(ellipsis);
    }
  }

  // Next Button
  const nextBtn = document.createElement("button");
  nextBtn.className = "page-btn";
  nextBtn.innerHTML = "&raquo;";
  nextBtn.disabled = state.page >= state.totalPages;
  nextBtn.title = "Next page";
  nextBtn.addEventListener("click", () => {
    if (state.page < state.totalPages) {
      state.page++;
      loadStudents();
    }
  });
  DOM.paginationControls.appendChild(nextBtn);
}

// ==========================================
// ACTION HANDLERS: VIEW, CREATE, EDIT, DELETE
// ==========================================

/**
 * Open View Student Profile modal.
 */
async function handleViewStudent(studentId) {
  openModal(DOM.viewModal);
  DOM.viewModalBody.innerHTML = `
    <div style="text-align: center; padding: 2rem;">
      <span class="spinner spinner-dark" style="width: 24px; height: 24px;"></span>
      <div style="margin-top: 0.5rem; color: var(--text-muted);">Loading profile...</div>
    </div>
  `;

  try {
    const student = await window.ApiService.getStudent(studentId);
    state.selectedStudent = student;

    const initials = getInitials(student.name);
    DOM.viewModalBody.innerHTML = `
      <div class="profile-card">
        <div class="profile-top">
          <div class="profile-avatar-large">${initials}</div>
          <div class="profile-info">
            <h4>${student.name}</h4>
            <p>ID #${student.id} &bull; ${student.course || "No Course Specified"}</p>
          </div>
        </div>

        <div class="detail-row">
          <span class="detail-label">Email Address:</span>
          <span class="detail-value"><a href="mailto:${student.email}" style="color: var(--primary);">${student.email}</a></span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Phone Number:</span>
          <span class="detail-value">${student.phone || "Not provided"}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Date of Birth:</span>
          <span class="detail-value">${formatDate(student.date_of_birth)}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Course:</span>
          <span class="detail-value">${student.course ? `<span class="badge badge-course">${student.course}</span>` : "Not assigned"}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Enrollment Date:</span>
          <span class="detail-value">${formatDate(student.enrollment_date)}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Residential Address:</span>
          <span class="detail-value">${student.address || "Not provided"}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Record Created:</span>
          <span class="detail-value" style="font-size: 0.8rem; color: var(--text-muted);">${formatTimestamp(student.created_at)}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Last Updated:</span>
          <span class="detail-value" style="font-size: 0.8rem; color: var(--text-muted);">${formatTimestamp(student.updated_at)}</span>
        </div>
      </div>
    `;
  } catch (err) {
    DOM.viewModalBody.innerHTML = `
      <div style="color: var(--danger); padding: 1.5rem; text-align: center;">
        Failed to load student profile: ${err.message}
      </div>
    `;
    showToast("Error", err.message, "error");
  }
}

/**
 * Handle Add Student Form Submission.
 */
DOM.addForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  setButtonLoading(DOM.submitAddBtn, true, "Create Student");

  const payload = {
    name: document.getElementById("add-name").value.trim(),
    date_of_birth: document.getElementById("add-dob").value,
    email: document.getElementById("add-email").value.trim(),
    phone: document.getElementById("add-phone").value.trim() || null,
    course: document.getElementById("add-course").value.trim() || null,
    enrollment_date: document.getElementById("add-enrollment").value || null,
    address: document.getElementById("add-address").value.trim() || null,
  };

  try {
    const created = await window.ApiService.createStudent(payload);
    showToast("Student Added!", `Record for ${created.name} was successfully created.`, "success");
    closeModal(DOM.addModal);
    DOM.addForm.reset();

    // Reload list and stats
    await Promise.all([loadStudents(), loadStats()]);
  } catch (err) {
    showToast("Failed to Add Student", err.message, "error");
  } finally {
    setButtonLoading(DOM.submitAddBtn, false, "Create Student");
  }
});

/**
 * Open Edit Student modal and populate fields.
 */
async function handleEditStudent(studentId) {
  openModal(DOM.editModal);
  DOM.editForm.reset();
  setButtonLoading(DOM.submitEditBtn, true, "Update Student");

  try {
    const student = await window.ApiService.getStudent(studentId);
    state.selectedStudent = student;

    document.getElementById("edit-id").value = student.id;
    document.getElementById("edit-name").value = student.name || "";
    document.getElementById("edit-dob").value = student.date_of_birth || "";
    document.getElementById("edit-email").value = student.email || "";
    document.getElementById("edit-phone").value = student.phone || "";
    document.getElementById("edit-course").value = student.course || "";
    document.getElementById("edit-enrollment").value = student.enrollment_date || "";
    document.getElementById("edit-address").value = student.address || "";
  } catch (err) {
    closeModal(DOM.editModal);
    showToast("Failed to Load Record", err.message, "error");
  } finally {
    setButtonLoading(DOM.submitEditBtn, false, "Update Student");
  }
}

/**
 * Handle Edit Student Form Submission.
 */
DOM.editForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("edit-id").value;
  setButtonLoading(DOM.submitEditBtn, true, "Update Student");

  const payload = {
    name: document.getElementById("edit-name").value.trim(),
    date_of_birth: document.getElementById("edit-dob").value,
    email: document.getElementById("edit-email").value.trim(),
    phone: document.getElementById("edit-phone").value.trim() || null,
    course: document.getElementById("edit-course").value.trim() || null,
    enrollment_date: document.getElementById("edit-enrollment").value || null,
    address: document.getElementById("edit-address").value.trim() || null,
  };

  try {
    const updated = await window.ApiService.updateStudent(id, payload);
    showToast("Student Updated!", `Record #${updated.id} (${updated.name}) has been updated.`, "success");
    closeModal(DOM.editModal);

    // Reload list and stats
    await Promise.all([loadStudents(), loadStats()]);
  } catch (err) {
    showToast("Update Failed", err.message, "error");
  } finally {
    setButtonLoading(DOM.submitEditBtn, false, "Update Student");
  }
});

/**
 * Prompt delete confirmation modal.
 */
function handleDeletePrompt(id, name) {
  state.deleteTargetId = id;
  DOM.deleteStudentName.textContent = name || "Student";
  DOM.deleteStudentId.textContent = `Record ID: #${id}`;
  openModal(DOM.deleteModal);
}

/**
 * Confirm student deletion.
 */
DOM.confirmDeleteBtn.addEventListener("click", async () => {
  if (!state.deleteTargetId) return;

  setButtonLoading(DOM.confirmDeleteBtn, true, "Delete Record");
  try {
    await window.ApiService.deleteStudent(state.deleteTargetId);
    showToast("Record Deleted", `Student #${state.deleteTargetId} has been removed.`, "success");
    closeModal(DOM.deleteModal);

    // If current page is now empty and not page 1, step back
    if (state.students.length === 1 && state.page > 1) {
      state.page--;
    }

    await Promise.all([loadStudents(), loadStats()]);
  } catch (err) {
    showToast("Delete Failed", err.message, "error");
  } finally {
    setButtonLoading(DOM.confirmDeleteBtn, false, "Delete Record");
    state.deleteTargetId = null;
  }
});

// ==========================================
// SEARCH, FILTER, AND SORT EVENT LISTENERS
// ==========================================

let searchDebounceTimer = null;
DOM.searchInput.addEventListener("input", (e) => {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    state.search = e.target.value.trim();
    state.page = 1;
    loadStudents();
  }, 300);
});

DOM.courseFilter.addEventListener("change", (e) => {
  state.course = e.target.value;
  state.page = 1;
  loadStudents();
});

DOM.sortBy.addEventListener("change", (e) => {
  state.sortBy = e.target.value;
  loadStudents();
});

DOM.sortOrder.addEventListener("change", (e) => {
  state.order = e.target.value;
  loadStudents();
});

DOM.clearFiltersBtn.addEventListener("click", () => {
  DOM.searchInput.value = "";
  DOM.courseFilter.value = "all";
  DOM.sortBy.value = "id";
  DOM.sortOrder.value = "desc";

  state.search = "";
  state.course = "all";
  state.sortBy = "id";
  state.order = "desc";
  state.page = 1;

  loadStudents();
});

// ==========================================
// BUTTON EVENT ATTACHMENTS
// ==========================================

// Add modal triggers
DOM.openAddModalBtn.addEventListener("click", () => {
  DOM.addForm.reset();
  // Default enrollment date to today
  document.getElementById("add-enrollment").value = new Date().toISOString().split("T")[0];
  openModal(DOM.addModal);
});

DOM.emptyAddBtn.addEventListener("click", () => {
  DOM.addForm.reset();
  document.getElementById("add-enrollment").value = new Date().toISOString().split("T")[0];
  openModal(DOM.addModal);
});

DOM.closeAddModal.addEventListener("click", () => closeModal(DOM.addModal));
DOM.cancelAddBtn.addEventListener("click", () => closeModal(DOM.addModal));

// Edit modal cancel / close
DOM.closeEditModal.addEventListener("click", () => closeModal(DOM.editModal));
DOM.cancelEditBtn.addEventListener("click", () => closeModal(DOM.editModal));

// View modal cancel / close
DOM.closeViewModal.addEventListener("click", () => closeModal(DOM.viewModal));
DOM.closeViewBtn.addEventListener("click", () => closeModal(DOM.viewModal));
DOM.viewEditShortcutBtn.addEventListener("click", () => {
  if (state.selectedStudent) {
    closeModal(DOM.viewModal);
    handleEditStudent(state.selectedStudent.id);
  }
});

// Delete modal cancel / close
DOM.closeDeleteModal.addEventListener("click", () => closeModal(DOM.deleteModal));
DOM.cancelDeleteBtn.addEventListener("click", () => closeModal(DOM.deleteModal));

// Refresh button
DOM.refreshBtn.addEventListener("click", async () => {
  try {
    DOM.refreshBtn.disabled = true;
    await Promise.all([loadStudents(), loadStats(), checkBackendHealth()]);
    showToast("Database Synced", "All student records are up to date.", "success");
  } finally {
    DOM.refreshBtn.disabled = false;
  }
});

// Mobile menu toggle
DOM.menuToggle.addEventListener("click", () => {
  DOM.sidebar.classList.toggle("open");
  DOM.sidebarBackdrop.classList.toggle("show");
});

DOM.sidebarBackdrop.addEventListener("click", () => {
  DOM.sidebar.classList.remove("open");
  DOM.sidebarBackdrop.classList.remove("show");
});

// ==========================================
// BACKEND HEALTH CHECK
// ==========================================

async function checkBackendHealth() {
  try {
    const health = await window.ApiService.getHealth();
    if (health.status === "healthy") {
      DOM.backendStatusText.textContent = "Backend Online";
      DOM.backendStatusText.style.color = "var(--text-light)";
    } else {
      DOM.backendStatusText.textContent = `Degraded (${health.database})`;
      DOM.backendStatusText.style.color = "var(--warning)";
    }
  } catch (err) {
    DOM.backendStatusText.textContent = "Offline / Disconnected";
    DOM.backendStatusText.style.color = "var(--danger)";
    console.warn("Backend health check failed:", err.message);
  }
}

// ==========================================
// APPLICATION INITIALIZATION
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
  // Check health, load statistics and initial student list
  checkBackendHealth();
  loadStats();
  loadStudents();

  // Periodic health check every 30 seconds
  setInterval(checkBackendHealth, 30000);
});
