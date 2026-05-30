document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const systemBadgeText = document.getElementById("system-badge-text");
    const statusPulse = document.getElementById("status-pulse");
    const mainStatusCard = document.getElementById("main-status-card");
    const statusIconContainer = document.getElementById("status-icon-container");
    const statusIcon = document.getElementById("status-icon");
    const statusText = document.getElementById("status-text");
    const statusDescText = document.getElementById("status-desc-text");
    
    const lastScrapedTime = document.getElementById("last-scraped-time");
    const noticesCount = document.getElementById("notices-count");
    
    const loadingSpinner = document.getElementById("loading-spinner");
    const emptyState = document.getElementById("empty-state");
    const announcementsContainer = document.getElementById("announcements-container");
    
    // Modal Elements
    const noticeModal = document.getElementById("notice-modal");
    const closeModalBtn = document.getElementById("close-modal-btn");
    const modalNumBadge = document.getElementById("modal-num-badge");
    const modalTitle = document.getElementById("modal-title");
    const modalWriter = document.getElementById("modal-writer");
    const modalDate = document.getElementById("modal-date");
    const modalViews = document.getElementById("modal-views");
    const modalBodyContent = document.getElementById("modal-body-content");

    // Local announcements list copy to read notice bodies from when cards are clicked
    let noticesData = [];

    // Cache-busting helper
    const getCacheBusterUrl = (basePath) => `${basePath}?t=${Date.now()}`;

    // Initialize Dashboard
    async function initDashboard() {
        try {
            // Fetch Status data
            const statusResponse = await fetch(getCacheBusterUrl('/data/status.json'));
            if (!statusResponse.ok) throw new Error("Status file not found");
            const status = await statusResponse.json();
            
            // Fetch Announcements data
            const noticesResponse = await fetch(getCacheBusterUrl('/data/notices.json'));
            if (!noticesResponse.ok) throw new Error("Notices file not found");
            noticesData = await noticesResponse.json();

            // 1. Update Status Card and Header Badge
            updateSystemStatus(status);

            // 2. Update Notices List
            renderNotices(noticesData);

        } catch (error) {
            console.error("Error loading dashboard data:", error);
            showFallbackState(error.message);
        }
    }

    // Update Status Card View
    function updateSystemStatus(data) {
        const isOperational = data.status === "Operational" && data.last_success === true;
        
        // Header badge
        systemBadgeText.textContent = isOperational ? "시스템정상 (Operational)" : "점검 필요 (Degraded)";
        statusPulse.className = `pulse-indicator ${isOperational ? 'green' : 'red'}`;
        
        // Status Card
        mainStatusCard.className = `status-card glow-card ${isOperational ? 'operational' : 'degraded'}`;
        statusIconContainer.className = `card-icon ${isOperational ? 'status-ok' : 'status-error'}`;
        statusIcon.className = isOperational ? "fa-solid fa-circle-check" : "fa-solid fa-circle-exclamation";
        
        statusText.textContent = isOperational ? "정상 작동 중" : "모니터링 점검 필요";
        statusText.className = `status-value ${isOperational ? 'green' : 'red'}`;
        
        statusDescText.textContent = isOperational 
            ? "모니터링 에이전트가 정상 작동하며 공지사항을 감시하고 있습니다." 
            : `경고: ${data.error_message || "모니터링 스크립트 실행 오류가 감지되었습니다."}`;

        // Last Scraped and Count
        lastScrapedTime.textContent = formatScrapedTime(data.last_scraped);
        noticesCount.textContent = `${data.total_notices || 0} 개`;
    }

    // Format Scraped Time String to be human readable
    function formatScrapedTime(timeStr) {
        if (!timeStr) return "알 수 없음";
        // Just return the string as is since the backend generates beautiful KST timestamps
        return timeStr;
    }

    // Render announcements to list
    function renderNotices(notices) {
        // Hide loader
        loadingSpinner.classList.add("hidden");

        if (!notices || notices.length === 0) {
            emptyState.classList.remove("hidden");
            announcementsContainer.classList.add("hidden");
            return;
        }

        emptyState.classList.add("hidden");
        announcementsContainer.classList.remove("hidden");
        announcementsContainer.innerHTML = ""; // Clear list

        notices.forEach((item, index) => {
            const card = document.createElement("div");
            card.className = "announcement-card";
            card.setAttribute("data-index", index);
            card.innerHTML = `
                <div class="announcement-card-content">
                    <div class="notice-meta-top">
                        <span class="notice-num">No. ${item.num || item.rnum}</span>
                        <span class="notice-date">
                            <i class="fa-regular fa-calendar"></i> ${item.write_dt}
                        </span>
                    </div>
                    <h4 class="announcement-title" title="${item.title}">${item.title}</h4>
                    <div class="notice-meta-bottom">
                        <span class="notice-writer">
                            <i class="fa-solid fa-user-pen"></i> ${item.writer || "교육대학원"}
                        </span>
                        <span class="notice-views">
                            <i class="fa-regular fa-eye"></i> 조회수: ${item.cnt || 0}
                        </span>
                    </div>
                </div>
                <div class="arrow-icon">
                    <i class="fa-solid fa-chevron-right"></i>
                </div>
            `;

            // Card Click event to view full details
            card.addEventListener("click", () => {
                openNoticeModal(item);
            });

            announcementsContainer.appendChild(card);
        });
    }

    // Show Fallback State if JSON files are missing or fetch fails
    function showFallbackState(message) {
        loadingSpinner.classList.add("hidden");
        
        // Set degraded status
        systemBadgeText.textContent = "연결 오류 (Disconnected)";
        statusPulse.className = "pulse-indicator red";
        
        mainStatusCard.className = "status-card glow-card degraded";
        statusIconContainer.className = "card-icon status-error";
        statusIcon.className = "fa-solid fa-circle-exclamation";
        statusText.textContent = "데이터 없음";
        statusText.className = "status-value red";
        statusDescText.textContent = `오류: ${message}. 스크래퍼가 아직 동작하지 않았거나 로컬 데이터가 누락되었습니다.`;

        lastScrapedTime.textContent = "대기 중";
        noticesCount.textContent = "0 개";
        
        emptyState.innerHTML = `
            <i class="fa-solid fa-triangle-exclamation" style="font-size: 48px; color: var(--color-red);"></i>
            <h3 style="margin-top: 16px;">로컬 데이터 수집 대기 중</h3>
            <p style="color: var(--text-secondary); max-width: 500px; margin: 8px auto 0 auto; font-size: 14px;">
                서버에 수집된 공지사항 파일이 발견되지 않았습니다. GitHub Actions의 Cron 스크립트가 최초 실행되거나 <code>python scraper.py</code>가 완료되면 정상 작동합니다.
            </p>
        `;
        emptyState.classList.remove("hidden");
        announcementsContainer.classList.add("hidden");
    }

    // Open Notice Detail Modal
    function openNoticeModal(notice) {
        modalNumBadge.textContent = `No. ${notice.num}`;
        modalTitle.textContent = notice.title;
        modalWriter.textContent = notice.writer || "교육대학원";
        modalDate.textContent = notice.write_dt;
        modalViews.textContent = notice.cnt || 0;
        
        // Safely set notice body content
        // Clean up escaped double quotes in inline styles (often introduced by BS4 encoding test tools)
        let htmlBody = notice.cont_html || "<p style='color: var(--text-secondary); text-align: center; padding: 40px;'>본 공지사항은 요약된 텍스트 내용만 등록되어 있습니다.</p>";
        
        // Fix some typical JSP backslash escapes in style attributes to make it render cleanly in browsers
        htmlBody = htmlBody.replace(/\\"/g, '"').replace(/\\'/g, "'");
        
        modalBodyContent.innerHTML = htmlBody;

        // Show Modal
        noticeModal.classList.remove("hidden");
        document.body.style.overflow = "hidden"; // Disable background scrolling
    }

    // Close Notice Detail Modal
    function closeNoticeModal() {
        noticeModal.classList.add("hidden");
        document.body.style.overflow = ""; // Enable background scrolling
    }

    // Event Listeners for Modal
    closeModalBtn.addEventListener("click", closeNoticeModal);
    
    // Close modal when clicking outside the modal content card
    noticeModal.addEventListener("click", (e) => {
        if (e.target === noticeModal) {
            closeNoticeModal();
        }
    });

    // Close modal on Escape key press
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !noticeModal.classList.contains("hidden")) {
            closeNoticeModal();
        }
    });

    // Initial Trigger
    initDashboard();
});
