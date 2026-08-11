const CJE_BOARD_URL = 'https://www.cje.ac.kr/elder_edu/web/board/brdList.do?menu_cd=000017';
const CJE_NOTICE_STATE_KEY = 'cje_notice_known_ids_v1';
const CJE_ALERT_TO = 'dlfgns316ai@gmail.com';

function checkCjeGraduateNotices() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) {
    console.log('Another notice check is already running.');
    return;
  }

  try {
    const response = UrlFetchApp.fetch(CJE_BOARD_URL, {
      followRedirects: true,
      muteHttpExceptions: true,
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; CJE-Notice-Monitor/1.0)'
      }
    });
    const statusCode = response.getResponseCode();
    if (statusCode < 200 || statusCode >= 300) {
      throw new Error(`Notice board returned HTTP ${statusCode}`);
    }

    const payload = JSON.parse(response.getContentText('UTF-8'));
    if (!Array.isArray(payload.brdList)) {
      throw new Error("Invalid response: 'brdList' is missing");
    }

    const notices = payload.brdList
      .map(function(item) {
        return {
          id: String(item.num || '').trim(),
          title: String(item.title || '').trim(),
          writer: String(item.username || '교육대학원').trim(),
          date: String(item.write_dt || '').trim(),
          body: cleanNoticeText_(item.cont || '')
        };
      })
      .filter(function(item) {
        return item.id;
      });

    const properties = PropertiesService.getScriptProperties();
    const saved = properties.getProperty(CJE_NOTICE_STATE_KEY);
    const currentIds = notices.map(function(item) { return item.id; });

    if (!saved) {
      properties.setProperty(CJE_NOTICE_STATE_KEY, JSON.stringify(currentIds));
      console.log(`Baseline initialized with ${currentIds.length} notices.`);
      return;
    }

    const knownIds = new Set(JSON.parse(saved));
    const newNotices = notices.filter(function(item) {
      return !knownIds.has(item.id);
    });

    if (newNotices.length === 0) {
      console.log('No new notices.');
      return;
    }

    sendCjeNoticeDigest_(newNotices.slice().reverse());

    const updatedIds = Array.from(new Set(currentIds.concat(Array.from(knownIds)))).slice(0, 500);
    properties.setProperty(CJE_NOTICE_STATE_KEY, JSON.stringify(updatedIds));
    console.log(`Sent a Gmail alert for ${newNotices.length} new notice(s).`);
  } finally {
    lock.releaseLock();
  }
}

function setupCjeNoticeTrigger() {
  ScriptApp.getProjectTriggers()
    .filter(function(trigger) {
      return trigger.getHandlerFunction() === 'checkCjeGraduateNotices';
    })
    .forEach(function(trigger) {
      ScriptApp.deleteTrigger(trigger);
    });

  checkCjeGraduateNotices();

  ScriptApp.newTrigger('checkCjeGraduateNotices')
    .timeBased()
    .everyHours(3)
    .create();
}

function sendCjeSetupEmail() {
  MailApp.sendEmail({
    to: CJE_ALERT_TO,
    subject: '[알림] 청주교대 대학원 공지 모니터 설정 완료',
    body: [
      '청주교대 대학원 공지 모니터의 Gmail 발송 설정이 완료되었습니다.',
      '앞으로 3시간마다 새 공지를 확인하고, 새 글이 있을 때 이 주소로 알립니다.',
      '',
      CJE_BOARD_URL
    ].join('\n'),
    name: '청주교대 대학원 공지 알림'
  });
}

function sendCjeNoticeDigest_(notices) {
  const subject = notices.length === 1
    ? `[청주교대 대학원 새 공지] ${notices[0].title}`
    : `[청주교대 대학원 새 공지] ${notices.length}건`;

  const plainSections = notices.map(function(notice) {
    return [
      `제목: ${notice.title}`,
      `작성자: ${notice.writer}`,
      `등록일: ${notice.date}`,
      '',
      '내용 요약:',
      notice.body.slice(0, 8000) || '(내용 없음)'
    ].join('\n');
  });

  const htmlSections = notices.map(function(notice) {
    const body = escapeHtml_(notice.body.slice(0, 8000) || '(내용 없음)').replace(/\n/g, '<br>');
    return [
      '<section style="margin:0 0 24px;padding:16px;border:1px solid #e5e7eb;border-radius:10px">',
      `<h2 style="margin-top:0;color:#1d4ed8">${escapeHtml_(notice.title)}</h2>`,
      `<p><strong>작성자:</strong> ${escapeHtml_(notice.writer)}<br>`,
      `<strong>등록일:</strong> ${escapeHtml_(notice.date)}</p>`,
      `<div style="padding:14px;background:#f3f4f6;border-radius:8px">${body}</div>`,
      '</section>'
    ].join('');
  });

  MailApp.sendEmail({
    to: CJE_ALERT_TO,
    subject: subject,
    body: [
      '청주교대 대학원에 새 공지가 등록되었습니다.',
      '',
      plainSections.join('\n\n--------------------\n\n'),
      '',
      `전체 게시판: ${CJE_BOARD_URL}`
    ].join('\n'),
    htmlBody: [
      '<div style="font-family:Arial,\'Malgun Gothic\',sans-serif;line-height:1.6;color:#1f2937">',
      '<h1 style="font-size:22px">🔔 청주교대 대학원 새 공지</h1>',
      htmlSections.join(''),
      `<p><a href="${CJE_BOARD_URL}">전체 게시판 보러가기</a></p>`,
      '</div>'
    ].join(''),
    name: '청주교대 대학원 공지 알림'
  });
}

function cleanNoticeText_(value) {
  return String(value || '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>/gi, '\n')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .split('\n')
    .map(function(line) { return line.replace(/\s+/g, ' ').trim(); })
    .filter(Boolean)
    .join('\n');
}

function escapeHtml_(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
