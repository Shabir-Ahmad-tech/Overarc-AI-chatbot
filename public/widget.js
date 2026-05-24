(function () {
  // =========================================================================
  // 1. EXTRACT BOT CONFIGURATION
  // =========================================================================
  const scriptEl = document.currentScript;
  if (!scriptEl) return;
  const scriptUrl = new URL(scriptEl.src);
  const botId = scriptUrl.searchParams.get("botId") || "clinic";
  const baseUrl = scriptUrl.origin;

  // =========================================================================
  // 2. STATE MANAGEMENT
  // =========================================================================
  const state = {
    isOpen: false,
    config: null,
    messageCount: 0,
    leadCaptured: false,
    leadFormShown: false,
    chatHistory: [],
    leads: []
  };

  // =========================================================================
  // 3. FETCH CONFIGURATION & INITIALIZE
  // =========================================================================
  fetch(`${baseUrl}/api/widget-config?botId=${botId}`)
    .then(res => {
      if (!res.ok) throw new Error("Business not found");
      return res.json();
    })
    .then(config => {
      state.config = config;
      injectStyles();
      buildMarkup();
      initEvents();
      loadLucide();
    })
    .catch(err => console.error("SmartBot Embed Error:", err));

  // =========================================================================
  // 4. STYLE INJECTION (DYNAMICS ACCENT THEMING)
  // =========================================================================
  function injectStyles() {
    const color = state.config.color || "#10B981";
    const darkColor = state.config.dark_color || "#059669";
    const styleEl = document.createElement("style");
    styleEl.innerHTML = `
      #sb-widget-bubble {
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, ${color} 0%, ${darkColor} 100%);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999998;
        border: none;
        transition: transform 0.2s ease-in-out;
      }
      #sb-widget-bubble:hover {
        transform: scale(1.08);
      }
      #sb-widget-bubble svg {
        width: 26px;
        height: 26px;
        color: #ffffff;
        transition: transform 0.2s ease-in-out;
      }
      #sb-widget-window {
        position: fixed;
        bottom: 96px;
        right: 24px;
        width: 380px;
        height: 560px;
        border-radius: 16px;
        background: #111111;
        border: 1px solid rgba(255,255,255,0.07);
        box-shadow: 0 12px 48px rgba(0,0,0,0.5);
        z-index: 999999;
        display: none;
        flex-direction: column;
        overflow: hidden;
        font-family: 'Inter', system-ui, sans-serif;
        color: #f4f4f4;
        transition: opacity 0.2s ease-out, transform 0.2s ease-out;
        transform: translateY(12px);
        opacity: 0;
      }
      #sb-widget-window.open {
        display: flex;
        transform: translateY(0);
        opacity: 1;
      }
      .sb-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px;
        background: #181818;
        border-bottom: 1px solid rgba(255,255,255,0.07);
      }
      .sb-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, ${color}, ${darkColor});
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
      }
      .sb-title-area {
        flex: 1;
      }
      .sb-name {
        font-size: 15px;
        font-weight: 600;
        color: #f4f4f4;
      }
      .sb-status {
        font-size: 12px;
        color: #22c55e;
        display: flex;
        align-items: center;
        gap: 5px;
      }
      .sb-status::before {
        content: '';
        width: 7px;
        height: 7px;
        background: #22c55e;
        border-radius: 50%;
      }
      .sb-close {
        background: none;
        border: none;
        color: rgba(255,255,255,0.5);
        cursor: pointer;
        padding: 6px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .sb-close:hover {
        background: rgba(255,255,255,0.07);
        color: #ffffff;
      }
      .sb-messages {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      .sb-messages::-webkit-scrollbar {
        width: 4px;
      }
      .sb-messages::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
      }
      .sb-msg {
        display: flex;
        flex-direction: column;
      }
      .sb-msg.user { align-items: flex-end; }
      .sb-msg.bot  { align-items: flex-start; }
      .sb-bubble {
        max-width: 82%;
        padding: 10px 14px;
        font-size: 14px;
        line-height: 1.5;
        border-radius: 18px;
      }
      .sb-msg.user .sb-bubble {
        background: ${color};
        color: #ffffff;
        border-bottom-right-radius: 4px;
      }
      .sb-msg.bot .sb-bubble {
        background: #222222;
        color: #f4f4f4;
        border-bottom-left-radius: 4px;
      }
      .sb-time {
        font-size: 10px;
        color: rgba(255,255,255,0.4);
        margin-top: 4px;
        padding: 0 4px;
      }
      .sb-quick-replies {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 6px;
      }
      .sb-chip {
        background: transparent;
        border: 1px solid ${color};
        color: ${color};
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 12px;
        cursor: pointer;
        transition: background 0.2s, color 0.2s;
      }
      .sb-chip:hover {
        background: ${color};
        color: #ffffff;
      }
      .sb-input-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 16px;
        border-top: 1px solid rgba(255,255,255,0.07);
        background: #111111;
      }
      .sb-input {
        flex: 1;
        background: #1c1c1c;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 20px;
        padding: 10px 16px;
        color: #ffffff;
        font-size: 14px;
        outline: none;
      }
      .sb-input:focus {
        border-color: ${color};
      }
      .sb-send {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, ${color}, ${darkColor});
        border: none;
        color: #ffffff;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .sb-send:hover {
        transform: scale(1.05);
      }
      .sb-typing {
        display: flex;
        gap: 4px;
        padding: 10px 14px;
        background: #222222;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        width: fit-content;
      }
      .sb-dot {
        width: 7px;
        height: 7px;
        background: rgba(255,255,255,0.4);
        border-radius: 50%;
        animation: sb-bounce 1.2s infinite;
      }
      .sb-dot:nth-child(2) { animation-delay: 0.2s; }
      .sb-dot:nth-child(3) { animation-delay: 0.4s; }
      @keyframes sb-bounce {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-6px); }
      }
      .sb-lead-form {
        background: #181818;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 14px;
        margin-top: 6px;
        width: 100%;
        max-width: 280px;
      }
      .sb-lead-form p {
        font-size: 12px;
        color: rgba(255,255,255,0.6);
        margin-bottom: 10px;
      }
      .sb-lead-form input {
        width: 100%;
        background: #111111;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 6px;
        padding: 8px 10px;
        color: #ffffff;
        font-size: 13px;
        margin-bottom: 8px;
        outline: none;
      }
      .sb-lead-form input:focus {
        border-color: ${color};
      }
      .sb-lead-btn {
        width: 100%;
        background: linear-gradient(135deg, ${color}, ${darkColor});
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
      }
      .sb-brand {
        text-align: center;
        font-size: 10px;
        color: rgba(255,255,255,0.3);
        padding: 8px 0;
        background: #111111;
      }
      .sb-brand a {
        color: ${color};
        text-decoration: none;
      }
      @media (max-width: 480px) {
        #sb-widget-window {
          width: calc(100vw - 32px);
          height: calc(100vh - 120px);
          bottom: 80px;
          right: 16px;
        }
      }
      /* ============================================================
         RICH SERVICES / MENU DISPLAY
      ============================================================ */
      .rich-services-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 10px;
        width: 100%;
      }
      .rich-service-item {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px 14px;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        width: 100%;
        text-align: left;
      }
      .rich-service-item:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: ${color};
        transform: translateX(2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
      .rich-service-item.selected {
        border-color: ${color};
        background: rgba(255, 255, 255, 0.05);
      }
      .rich-service-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
        flex: 1;
        text-align: left;
      }
      .rich-service-name {
        font-size: 13.5px;
        font-weight: 600;
        color: #ffffff;
        line-height: 1.4;
      }
      .rich-service-price {
        font-size: 12px;
        font-weight: 700;
        color: ${color};
      }
      .rich-qty-controls {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2px;
      }
      .rich-qty-btn {
        background: transparent;
        border: none;
        color: #fff;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: bold;
        transition: background 0.2s;
      }
      .rich-qty-btn:hover {
        background: rgba(255, 255, 255, 0.1);
      }
      .rich-qty-btn.inc:hover {
        background: ${color};
      }
      .rich-qty-val {
        font-size: 13px;
        font-weight: 600;
        color: #fff;
        min-width: 14px;
        text-align: center;
      }
      .rich-cart-summary {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-left: 3px solid ${color};
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 14px;
        width: 100%;
        animation: slide-up 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: left;
      }
      @keyframes slide-up {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .rich-cart-details {
        display: flex;
        flex-direction: column;
        gap: 2px;
      }
      .rich-cart-count {
        font-size: 10px;
        color: rgba(255, 255, 255, 0.5);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
      }
      .rich-cart-total {
        font-size: 14px;
        font-weight: 700;
        color: #fff;
      }
      .rich-cart-submit-btn {
        background: ${color};
        color: #fff;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: opacity 0.2s, transform 0.2s;
      }
      .rich-cart-submit-btn:hover {
        opacity: 0.95;
        transform: translateY(-1px);
      }
      .rich-cart-submit-btn i {
        width: 12px;
        height: 12px;
      }
      .msg-text-part {
        margin-bottom: 8px;
        line-height: 1.5;
        width: 100%;
        text-align: left;
      }
      #sb-widget-window {
        --brand: ${color};
        --brand-dark: ${darkColor};
      }
    `;
    document.head.appendChild(styleEl);
  }

  // =========================================================================
  // 5. RENDER CHATMARKUP
  // =========================================================================
  function buildMarkup() {
    // 1. Chat Bubble
    const bubble = document.createElement("button");
    bubble.id = "sb-widget-bubble";
    bubble.setAttribute("aria-label", "Open Chat");
    bubble.innerHTML = `<i data-lucide="message-circle" id="sb-bubble-icon"></i>`;
    document.body.appendChild(bubble);

    // 2. Chat Window
    const win = document.createElement("div");
    win.id = "sb-widget-window";
    win.innerHTML = `
      <div class="sb-header">
        <div class="sb-avatar">${state.config.emoji || '💬'}</div>
        <div class="sb-title-area">
          <div class="sb-name">${state.config.name}</div>
          <div class="sb-status">Online</div>
        </div>
        <button class="sb-close" id="sb-widget-close" aria-label="Close Chat">
          <i data-lucide="x"></i>
        </button>
      </div>
      <div class="sb-messages" id="sb-widget-messages"></div>
      <div class="sb-input-bar">
        <input type="text" class="sb-input" id="sb-widget-input" placeholder="Type your message..." autocomplete="off" />
        <button class="sb-send" id="sb-widget-send" aria-label="Send">
          <i data-lucide="send"></i>
        </button>
      </div>
      <div class="sb-brand">Powered by <a href="${baseUrl}" target="_blank">Overarc</a></div>
    `;
    document.body.appendChild(win);
  }

  // =========================================================================
  // 6. EVENT INTERACTION
  // =========================================================================
  function initEvents() {
    const bubble = document.getElementById("sb-widget-bubble");
    const close = document.getElementById("sb-widget-close");
    const win = document.getElementById("sb-widget-window");
    const input = document.getElementById("sb-widget-input");
    const send = document.getElementById("sb-widget-send");

    const toggle = () => {
      state.isOpen = !state.isOpen;
      const icon = document.getElementById("sb-bubble-icon");
      if (state.isOpen) {
        win.style.display = "flex";
        setTimeout(() => win.classList.add("open"), 10);
        icon.setAttribute("data-lucide", "x");
        if (window.lucide) window.lucide.createIcons();
        
        if (state.messageCount === 0) {
          setTimeout(() => sendBotMessage(state.config.greeting, true), 300);
          setTimeout(() => renderQuickReplies(), 800);
        }
        input.focus();
      } else {
        win.classList.remove("open");
        setTimeout(() => win.style.display = "none", 200);
        icon.setAttribute("data-lucide", "message-circle");
        if (window.lucide) window.lucide.createIcons();
      }
    };

    bubble.onclick = toggle;
    close.onclick = toggle;

    send.onclick = () => {
      const txt = input.value.trim();
      if (txt) {
        input.value = "";
        handleUserInput(txt);
      }
    };

    input.onkeydown = (e) => {
      if (e.key === "Enter") {
        const txt = input.value.trim();
        if (txt) {
          input.value = "";
          handleUserInput(txt);
        }
      }
    };
  }

  // =========================================================================
  // 7. MESSAGE PIPELINE & XSS SAFETY
  // =========================================================================
  function escapeHTML(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  window.widgetHandleUserInput = handleUserInput;

  function parseRichServices(text, botId) {
    const lines = text.split('\n');
    const otherLines = [];
    
    const actionText = bId => {
      if (bId === 'restaurant') return 'Order';
      if (bId === 'clinic') return 'Book';
      if (bId === 'realestate') return 'Inquire';
      return 'Select';
    };

    const menuId = 'menu-' + Math.random().toString(36).substr(2, 9);
    window.widgetCarts = window.widgetCarts || {};
    window.widgetCarts[menuId] = {};

    let hasService = false;
    let serviceHtml = `<div class="rich-services-list">`;

    lines.forEach(line => {
      const trimmed = line.trim();
      const match = trimmed.match(/^[-*]\s+(.+?)\s*:\s*(.+)$/);
      if (match) {
        const name = match[1].replace(/\*\*/g, '').trim();
        const price = match[2].replace(/\*\*/g, '').trim();
        const action = actionText(botId);
        
        hasService = true;
        serviceHtml += `
          <div class="rich-service-item" data-name="${name}" data-price="${price}">
            <div class="rich-service-info">
              <div class="rich-service-name">${name}</div>
              <div class="rich-service-price">${price}</div>
            </div>
            <div class="rich-qty-controls">
              <button class="rich-qty-btn dec" onclick="event.stopPropagation(); window.changeWidgetQty('${menuId}', '${name.replace(/'/g, "\\'")}', -1, this)">-</button>
              <span class="rich-qty-val">0</span>
              <button class="rich-qty-btn inc" onclick="event.stopPropagation(); window.changeWidgetQty('${menuId}', '${name.replace(/'/g, "\\'")}', 1, this)">+</button>
            </div>
          </div>
        `;
      } else {
        otherLines.push(line);
      }
    });

    serviceHtml += `
      <div class="rich-cart-summary" id="summary-${menuId}" style="display: none;">
        <div class="rich-cart-details">
          <span class="rich-cart-count">0 items selected</span>
          <span class="rich-cart-total">Total: PKR 0</span>
        </div>
        <button class="rich-cart-submit-btn" onclick="window.submitWidgetCart('${menuId}')">
          <span>Confirm & Order</span>
          <i data-lucide="arrow-right"></i>
        </button>
      </div>
    `;

    serviceHtml += `</div>`;

    if (hasService) {
      const textBefore = otherLines.join('\n').trim();
      const formattedTextBefore = textBefore
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      return {
        hasService: true,
        html: (formattedTextBefore ? `<div class="msg-text-part">${formattedTextBefore}</div>` : '') + serviceHtml
      };
    }

    const sanitized = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
    return { hasService: false, html: sanitized.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') };
  }

  window.changeWidgetQty = function(menuId, itemName, delta, btnEl) {
    const cart = window.widgetCarts[menuId];
    cart[itemName] = cart[itemName] || { qty: 0, priceStr: '', priceVal: 0 };
    
    const rowEl = btnEl.closest('.rich-service-item');
    const priceStr = rowEl.getAttribute('data-price');
    const cleanPrice = parseInt(priceStr.replace(/[^0-9]/g, ''), 10) || 0;
    
    cart[itemName].qty = Math.max(0, cart[itemName].qty + delta);
    cart[itemName].priceStr = priceStr;
    cart[itemName].priceVal = cleanPrice;
    
    const qtySpan = rowEl.querySelector('.rich-qty-val');
    qtySpan.textContent = cart[itemName].qty;
    
    if (cart[itemName].qty > 0) {
      rowEl.classList.add('selected');
    } else {
      rowEl.classList.remove('selected');
    }
    
    let totalItems = 0;
    let totalPrice = 0;
    let currency = priceStr.match(/^[A-Za-z$]+/)?.[0] || 'PKR';
    
    for (const item in cart) {
      totalItems += cart[item].qty;
      totalPrice += cart[item].qty * cart[item].priceVal;
    }
    
    const summaryEl = document.getElementById(`summary-${menuId}`);
    if (totalItems > 0) {
      summaryEl.style.display = 'flex';
      summaryEl.querySelector('.rich-cart-count').textContent = `${totalItems} item${totalItems > 1 ? 's' : ''} selected`;
      summaryEl.querySelector('.rich-cart-total').textContent = `Total: ${currency} ${totalPrice.toLocaleString()}`;
    } else {
      summaryEl.style.display = 'none';
    }
  };

  window.submitWidgetCart = function(menuId) {
    const cart = window.widgetCarts[menuId];
    const selected = [];
    let totalPrice = 0;
    let currency = 'PKR';
    
    for (const item in cart) {
      if (cart[item].qty > 0) {
        selected.push(`${cart[item].qty}x ${item} (${cart[item].priceStr})`);
        totalPrice += cart[item].qty * cart[item].priceVal;
        currency = cart[item].priceStr.match(/^[A-Za-z$]+/)?.[0] || 'PKR';
      }
    }
    
    if (selected.length === 0) return;
    
    const action = botId === 'restaurant' ? 'order / reserve' :
                   botId === 'clinic' ? 'book' : 'inquire about';
                   
    const msg = `I would like to ${action}:\n${selected.join('\n')}\nTotal: ${currency} ${totalPrice.toLocaleString()}`;
    
    const summaryEl = document.getElementById(`summary-${menuId}`);
    if (summaryEl) summaryEl.remove();
    
    // Disable qty buttons in this menu instance to finalize choice
    const menuContainer = document.querySelector(`[id="summary-${menuId}"]`)?.closest('.rich-services-list') || document.getElementById(`summary-${menuId}`)?.parentNode;
    if (menuContainer) {
      menuContainer.querySelectorAll('.rich-qty-btn').forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.5';
        btn.style.cursor = 'not-allowed';
      });
    }
    
    const input = document.getElementById("sb-widget-input") || document.getElementById("chat-input");
    if (input) input.value = "";
    
    const qr = document.getElementById("sb-quick-replies") || document.getElementById("quick-replies");
    if (qr) qr.remove();
    
    window.widgetHandleUserInput(msg);
  };

  function appendMessage(role, text) {
    const container = document.getElementById("sb-widget-messages");
    const div = document.createElement("div");
    div.className = `sb-msg ${role}`;

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    let htmlContent = '';
    if (role === 'bot') {
      const parsed = parseRichServices(text, botId);
      htmlContent = parsed.html;
    } else {
      const sanitized = escapeHTML(text);
      htmlContent = sanitized.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    div.innerHTML = `
      <div class="sb-bubble">${htmlContent}</div>
      <div class="sb-time">${time}</div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;

    if (window.lucide) window.lucide.createIcons();

    state.chatHistory.push({ role: role === "bot" ? "assistant" : "user", content: text });

    if (role === "user" && state.messageCount >= 2 && !state.leadCaptured && !state.leadFormShown) {
      state.leadFormShown = true;
      setTimeout(() => renderLeadForm(), 1200);
    }
  }

  function sendBotMessage(text, isFirst = false) {
    const container = document.getElementById("sb-widget-messages");
    const typing = document.createElement("div");
    typing.className = "sb-msg bot";
    typing.id = "sb-typing-msg";
    typing.innerHTML = `
      <div class="sb-typing">
        <div class="sb-dot"></div>
        <div class="sb-dot"></div>
        <div class="sb-dot"></div>
      </div>
    `;
    container.appendChild(typing);
    container.scrollTop = container.scrollHeight;

    const delay = isFirst ? 400 : 1000 + Math.random() * 500;
    setTimeout(() => {
      typing.remove();
      appendMessage("bot", text);
      state.messageCount++;
    }, delay);
  }

  function renderQuickReplies() {
    const replies = state.config.quick_replies || [];
    if (!replies.length) return;

    const container = document.getElementById("sb-widget-messages");
    const div = document.createElement("div");
    div.className = "sb-quick-replies";
    div.id = "sb-quick-replies";

    replies.forEach(reply => {
      const btn = document.createElement("button");
      btn.className = "sb-chip";
      btn.textContent = reply;
      btn.onclick = () => {
        div.remove();
        handleUserInput(reply);
      };
      div.appendChild(btn);
    });

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

  // =========================================================================
  // 8. INPUT LOCKING & TRANSACTION IDEMPOTENCY
  // =========================================================================
  function lockInput() {
    const input = document.getElementById("sb-widget-input");
    const send = document.getElementById("sb-widget-send");
    if (input) {
      input.disabled = true;
      input.placeholder = "AI is thinking...";
    }
    if (send) {
      send.disabled = true;
      send.style.opacity = "0.5";
      send.style.pointerEvents = "none";
    }
  }

  function unlockInput() {
    const input = document.getElementById("sb-widget-input");
    const send = document.getElementById("sb-widget-send");
    if (input) {
      input.disabled = false;
      input.placeholder = "Type your message...";
      input.focus();
    }
    if (send) {
      send.disabled = false;
      send.style.opacity = "1";
      send.style.pointerEvents = "auto";
    }
  }

  async function handleUserInput(text) {
    if (!text.trim()) return;
    appendMessage("user", text);
    state.messageCount++;

    lockInput();
    
    // Call server API dynamic chat
    try {
      const res = await fetch(`${baseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bot: botId,
          message: text,
          history: state.chatHistory.slice(0, -1) // Avoid double appending current input
        })
      });

      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      
      const reply = data.reply;
      sendBotMessage(reply);
      unlockInput();
    } catch (err) {
      console.error("Chat error:", err);
      sendBotMessage("I'm having a small technical issue right now. Please contact us directly — our team is standing by!");
      unlockInput();
    }
  }

  // =========================================================================
  // 9. DYNAMIC LEAD CAPTURING SYSTEM
  // =========================================================================
  function renderLeadForm() {
    const container = document.getElementById("sb-widget-messages");
    appendMessage("bot", "By the way — can I get your **name and phone number** so our team can follow up with you directly? 😊");

    setTimeout(() => {
      const formDiv = document.createElement("div");
      formDiv.className = "sb-msg bot";
      formDiv.innerHTML = `
        <div class="sb-lead-form">
          <p>Leave your details and we'll reach out shortly:</p>
          <input type="text" id="sb-lead-name" placeholder="Your full name" autocomplete="off" />
          <input type="tel" id="sb-lead-phone" placeholder="Phone number" autocomplete="off" />
          <button class="sb-lead-btn" id="sb-lead-submit">Send Details</button>
        </div>
      `;
      container.appendChild(formDiv);
      container.scrollTop = container.scrollHeight;

      document.getElementById("sb-lead-submit").onclick = () => {
        const name = document.getElementById("sb-lead-name").value.trim();
        const phone = document.getElementById("sb-lead-phone").value.trim();

        if (!name || !phone) {
          alert("Please enter both name and phone number");
          return;
        }

        formDiv.remove();
        state.leadCaptured = true;

        // Post lead dynamically to server DB leads.json
        fetch(`${baseUrl}/api/leads`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: name,
            phone: phone,
            bot: botId,
            message: "Lead captured from embedded widget"
          })
        }).catch(err => console.error("Leads Sync Error:", err));

        appendMessage("bot", `Thank you, **${name}**! ✅ I've passed your details to our team. Someone will contact you at **${phone}** shortly. Is there anything else I can help you with?`);
      };
    }, 800);
  }

  // =========================================================================
  // 10. LOAD LUCIDE LIBRARY DYNAMICALLY
  // =========================================================================
  function loadLucide() {
    if (!window.lucide) {
      const script = document.createElement("script");
      script.src = "https://unpkg.com/lucide@latest/dist/umd/lucide.min.js";
      script.onload = () => {
        if (window.lucide) window.lucide.createIcons();
      };
      document.head.appendChild(script);
    } else {
      window.lucide.createIcons();
    }
  }
})();
