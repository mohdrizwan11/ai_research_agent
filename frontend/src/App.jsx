import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { jsPDF } from 'jspdf';
import { 
  MessageSquarePlus, Search, Edit2, Trash2, Pin, Star,
  Download, Copy, RotateCcw, Plus, Zap, AlignLeft, BookOpen, MessageCircle 
} from 'lucide-react';
import './index.css';

const SRCS = [
  {n:'arXiv', c:'#e97b2e'}, {n:'Semantic Scholar', c:'#1d6fa8'},
  {n:'OpenAlex', c:'#22c55e'}, {n:'CrossRef', c:'#9333ea'},
  {n:'Wikipedia', c:'#3366cc'}, {n:'DuckDuckGo', c:'#d62728'}
];

const STEPS = {
  n: ['📡 Querying knowledge sources...', '🔍 Retrieving relevant documents...', '⚙️ Processing content...', '🧠 Synthesising findings...', '📝 Generating report...'],
  d: ['🗺 Planning research angles...', '📡 Searching arXiv & Semantic Scholar...', '📖 Querying OpenAlex...', '🔗 Cross-referencing sources...', '🧠 Deep synthesis in progress...', '📝 Compiling comprehensive report...']
};

function App() {
  // --- Sidebar & Chats State ---
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [theme, setTheme] = useState('dark');

  // --- Current Chat State ---
  const [topic, setTopic] = useState('');
  const [inputVal, setInputVal] = useState('');
  const [mode, setMode] = useState('concise');
  const [deep, setDeep] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [report, setReport] = useState('');
  const [sources, setSources] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [followUp, setFollowUp] = useState('');
  const [followUpLoading, setFollowUpLoading] = useState(false);

  const chatEndRef = useRef(null);

  // Initialize from LocalStorage
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    const saved = localStorage.getItem('claude_research_chats');
    if (saved) {
      setChats(JSON.parse(saved));
    }
  }, [theme]);

  // Save to LocalStorage
  useEffect(() => {
    if (chats.length > 0) {
      localStorage.setItem('claude_research_chats', JSON.stringify(chats));
    }
  }, [chats]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const generateId = () => crypto.randomUUID ? crypto.randomUUID() : Date.now().toString();

  // --- Sidebar Logic ---
  const handleNewChat = () => {
    setTopic('');
    setInputVal('');
    setReport('');
    setSources([]);
    setChatHistory([]);
    setCurrentChatId(null);
  };

  const loadChat = (chat) => {
    setCurrentChatId(chat.id);
    setTopic(chat.topic);
    setInputVal(chat.topic);
    setMode(chat.mode);
    setDeep(chat.deep || false);
    setReport(chat.report);
    setSources(chat.sources || []);
    setChatHistory(chat.chatHistory || []);
  };

  const updateChatState = (id, updates) => {
    setChats(prev => prev.map(c => c.id === id ? { ...c, ...updates } : c));
  };

  const togglePin = (id, e) => {
    e.stopPropagation();
    const chat = chats.find(c => c.id === id);
    updateChatState(id, { is_pinned: !chat.is_pinned });
  };

  const toggleStar = (id, e) => {
    e.stopPropagation();
    const chat = chats.find(c => c.id === id);
    updateChatState(id, { is_starred: !chat.is_starred });
  };

  const handleRename = (id, e) => {
    e.stopPropagation();
    const newTitle = prompt('Enter new chat title:');
    if (newTitle && newTitle.trim()) {
      updateChatState(id, { title: newTitle.trim() });
    }
  };

  const deleteChat = (id, e) => {
    e.stopPropagation();
    updateChatState(id, { is_deleted: true });
    if (currentChatId === id) {
      handleNewChat();
    }
  };

  const saveCurrentChat = () => {
    if (!topic || !report) return;
    
    if (currentChatId) {
      // Update existing
      updateChatState(currentChatId, {
        topic, mode, deep, report, sources, chatHistory
      });
    } else {
      // Create new
      const newId = generateId();
      const newChat = {
        id: newId,
        title: topic.slice(0, 30) + (topic.length > 30 ? '...' : ''),
        is_starred: false,
        is_pinned: false,
        is_deleted: false,
        created_at: new Date().toISOString(),
        topic, mode, deep, report, sources, chatHistory
      };
      setChats(prev => [newChat, ...prev]);
      setCurrentChatId(newId);
    }
  };

  // Run saveCurrentChat whenever report or chatHistory changes meaningfully
  useEffect(() => {
    if (report && !loading) {
      saveCurrentChat();
    }
  }, [report, chatHistory, loading]);

  // --- Research Logic ---
  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!inputVal.trim()) return;

    setTopic(inputVal.trim());
    setLoading(true);
    setReport('');
    setChatHistory([]);
    setSources([]);
    setLoadingStep(0);

    const stepsArray = deep ? STEPS.d : STEPS.n;
    
    const interval = setInterval(() => {
      setLoadingStep(prev => (prev < stepsArray.length - 1 ? prev + 1 : prev));
    }, deep ? 1500 : 1000);

    try {
      const response = await fetch(`http://localhost:8000/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: inputVal.trim(),
          mode: mode,
          deep_research: deep
        })
      });

      if (!response.ok) throw new Error(`Error: ${response.statusText}`);
      
      const data = await response.json();
      setReport(data.report || "No report generated.");
      
      const activeSources = data.sources && data.sources.length > 0 
        ? data.sources.map(s => s.source_type) 
        : [];
        
      const matchedSources = SRCS.filter(s => activeSources.includes(s.n.toLowerCase().replace(/\s/g, '')) || 
                                             (deep && (s.n === 'OpenAlex' || s.n === 'Semantic Scholar')));
      
      setSources(matchedSources.length > 0 ? matchedSources : SRCS.slice(0, deep ? 5 : 3));
      
      setChatHistory([
        { role: 'user', content: `Research topic: ${inputVal.trim()}` },
        { role: 'assistant', content: data.report || "Done." }
      ]);

    } catch (err) {
      setReport(`**Error**: ${err.message}`);
    } finally {
      clearInterval(interval);
      setLoading(false);
      setLoadingStep(stepsArray.length);
    }
  };

  const handleFollowUp = async (e) => {
    e.preventDefault();
    if (!followUp.trim() || !report) return;

    const query = followUp.trim();
    setFollowUp('');
    
    const newHistory = [...chatHistory, { role: 'user', content: query }];
    setChatHistory(newHistory);
    setFollowUpLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: topic,
          messages: newHistory
        })
      });
      if (!response.ok) throw new Error("Failed to get response");
      
      const data = await response.json();
      setChatHistory([...newHistory, { role: 'assistant', content: data.reply }]);
    } catch (err) {
      setChatHistory([...newHistory, { role: 'assistant', content: `Error: ${err.message}` }]);
    } finally {
      setFollowUpLoading(false);
    }
  };

  // --- Helpers ---
  const downloadPDF = () => {
    if (!report) return;
    const doc = new jsPDF({ unit: 'mm', format: 'a4' });
    const ml = 20, mr = 20, pw = 210, uw = pw - ml - mr;
    let y = ml;

    const checkPage = (h) => { if (y + h > 282) { doc.addPage(); y = ml; } };

    doc.setFillColor(184, 124, 24); doc.rect(0, 0, 210, 7, 'F');
    y = 18;
    doc.setFont('helvetica', 'bold'); doc.setFontSize(19); doc.setTextColor(30, 20, 10);
    const titleLines = doc.splitTextToSize(topic, uw);
    doc.text(titleLines, ml, y); y += titleLines.length * 9 + 3;

    doc.setFont('helvetica', 'normal'); doc.setFontSize(9); doc.setTextColor(140, 130, 115);
    const modeLabel = { short: 'Short Overview', concise: 'Concise Report', lengthy: 'Comprehensive Report' }[mode];
    doc.text(`${modeLabel}${deep ? ' · Deep Research' : ''}  ·  ${new Date().toLocaleDateString()}`, ml, y);
    y += 5; doc.setDrawColor(225, 215, 200); doc.line(ml, y, pw - mr, y); y += 8;

    const plain = report
      .replace(/^#{1,6}\s+(.+)$/gm, (_, t) => `\n\n${t.toUpperCase()}\n`)
      .replace(/\*\*(.+?)\*\*/g, '$1').replace(/\*(.+?)\*/g, '$1')
      .replace(/^[-*]\s+/gm, '•  ').replace(/\n{3,}/g, '\n\n').trim();

    for (const seg of plain.split(/\n\n+/)) {
      const l = seg.trim(); if (!l) continue;
      const isHeader = l === l.toUpperCase() && l.length < 70 && !l.startsWith('•');
      
      if (isHeader) {
        checkPage(14);
        doc.setFont('helvetica', 'bold'); doc.setFontSize(10); doc.setTextColor(184, 124, 24);
        doc.text(l, ml, y); y += 6;
        doc.setDrawColor(235, 220, 190); doc.line(ml, y, pw - mr, y); y += 5;
      } else {
        doc.setFont('helvetica', 'normal'); doc.setFontSize(10); doc.setTextColor(30, 25, 20);
        const textLines = doc.splitTextToSize(l, uw);
        for (const line of textLines) { checkPage(5.5); doc.text(line, ml, y); y += 5.5; }
        y += 3;
      }
    }

    const pgs = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pgs; i++) {
      doc.setPage(i);
      doc.setFillColor(250, 247, 242); doc.rect(0, 287, 210, 10, 'F');
      doc.setFont('helvetica', 'normal'); doc.setFontSize(7.5); doc.setTextColor(165, 155, 140);
      doc.text('ResearchAI · Autonomous Research Agent', ml, 293);
      doc.text(`Page ${i} of ${pgs}`, pw - mr, 293, { align: 'right' });
    }
    doc.save(`research_${topic.replace(/[^a-z0-9]/gi, '_').toLowerCase().slice(0, 30)}.pdf`);
  };

  const handleCopy = (e) => {
    navigator.clipboard.writeText(report);
    const btn = e.currentTarget;
    const originalText = btn.innerHTML;
    btn.innerHTML = '✓ Copied!';
    setTimeout(() => btn.innerHTML = originalText, 2000);
  };

  // --- Rendering Sidebar Items ---
  const activeChats = chats.filter(c => !c.is_deleted);
  const pinnedChats = activeChats.filter(c => c.is_pinned);
  const starredChats = activeChats.filter(c => c.is_starred && !c.is_pinned);
  const recentChats = activeChats.filter(c => !c.is_pinned && !c.is_starred);
  const filteredChats = activeChats.filter(c => c.title.toLowerCase().includes(searchQuery.toLowerCase()));

  const renderSidebarItem = (chat) => (
    <div 
      key={chat.id} 
      className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
      onClick={() => loadChat(chat)}
    >
      <div className="chat-item-title">{chat.title}</div>
      <div className="chat-item-actions" onClick={e => e.stopPropagation()}>
        <button className="action-btn" onClick={(e) => togglePin(chat.id, e)} title="Pin">
          <Pin size={12} fill={chat.is_pinned ? "currentColor" : "none"} />
        </button>
        <button className="action-btn" onClick={(e) => toggleStar(chat.id, e)} title="Star">
          <Star size={12} fill={chat.is_starred ? "currentColor" : "none"} />
        </button>
        <button className="action-btn" onClick={(e) => handleRename(chat.id, e)} title="Rename">
          <Edit2 size={12} />
        </button>
        <button className="action-btn" onClick={(e) => deleteChat(chat.id, e)} title="Delete">
          <Trash2 size={12} />
        </button>
      </div>
    </div>
  );

  return (
    <>
      <div className="sidebar">
        <button className="new-chat-btn" onClick={handleNewChat}>
          <MessageSquarePlus size={16} /> New Research
        </button>
        
        <div className="search-container">
          <Search size={14} className="search-icon" />
          <input 
            type="text" 
            className="search-input" 
            placeholder="Search chats..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="sidebar-scroll">
          {searchQuery ? (
            <div className="sidebar-section">
              <div className="section-header">Search Results</div>
              {filteredChats.map(renderSidebarItem)}
            </div>
          ) : (
            <>
              {pinnedChats.length > 0 && (
                <div className="sidebar-section">
                  <div className="section-header">Pinned</div>
                  {pinnedChats.map(renderSidebarItem)}
                </div>
              )}
              {starredChats.length > 0 && (
                <div className="sidebar-section">
                  <div className="section-header">Starred</div>
                  {starredChats.map(renderSidebarItem)}
                </div>
              )}
              {recentChats.length > 0 && (
                <div className="sidebar-section">
                  <div className="section-header">Recent</div>
                  {recentChats.map(renderSidebarItem)}
                </div>
              )}
            </>
          )}
        </div>

        <div className="theme-toggle-container">
          <button className="theme-toggle-btn" onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}>
            {theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode'}
          </button>
        </div>
      </div>

      <div className="main-content">
        <div className="wrap">
          <div className="hd">
            <div className="logo">[ Research<em>AI</em> ]</div>
            <div className="logo-sub">Autonomous · Multi-Source · Agentic</div>
          </div>

          {!report && !loading && (
            <div className="sugs">
              {['Transformer architecture', 'CRISPR gene editing', 'Quantum computing', 'Climate change mitigation'].map(s => (
                <button key={s} className="sug" onClick={() => { setInputVal(s); }}>{s}</button>
              ))}
            </div>
          )}

          <div className="sc">
            <textarea 
              className="sta" 
              rows="2"
              placeholder="Enter a research question… e.g. 'Impact of large language models on scientific discovery'"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSearch(); } }}
            ></textarea>
            <div className="sr">
              <div className="lc">
                <div className="mg">
                  <button type="button" className={`mp ${mode === 'short' ? 'on' : ''}`} onClick={() => setMode('short')}><Zap size={12} style={{display:'inline', marginRight:4, verticalAlign:'-2px'}}/> Short</button>
                  <button type="button" className={`mp ${mode === 'concise' ? 'on' : ''}`} onClick={() => setMode('concise')}><AlignLeft size={12} style={{display:'inline', marginRight:4, verticalAlign:'-2px'}}/> Concise</button>
                  <button type="button" className={`mp ${mode === 'lengthy' ? 'on' : ''}`} onClick={() => setMode('lengthy')}><BookOpen size={12} style={{display:'inline', marginRight:4, verticalAlign:'-2px'}}/> Lengthy</button>
                </div>
                <button type="button" className={`db ${deep ? 'on' : ''}`} onClick={() => setDeep(!deep)}>
                  <Plus size={14} className="di" style={{marginRight: 4}}/>
                  <span>Deep Research</span>
                </button>
              </div>
              <button type="button" className="gb" onClick={handleSearch} disabled={loading || !inputVal.trim()}>
                {loading ? 'Thinking...' : 'Research →'}
              </button>
            </div>
          </div>

          {loading && (
            <div className="res show">
              <div className="lc2">
                {(deep ? STEPS.d : STEPS.n).map((stepText, idx) => (
                  idx <= loadingStep ? (
                    <div key={idx} className="ls">
                      {idx < loadingStep ? <div className="dd">✓</div> : <div className="sp"></div>}
                      <span>{stepText}</span>
                    </div>
                  ) : null
                ))}
              </div>
            </div>
          )}

          {report && !loading && (
            <div className="res show">
              <div className="rm">
                <div className="rt">{topic}</div>
                <span className="badge bm">
                  {mode === 'short' && '⚡ Short'}
                  {mode === 'concise' && '📋 Concise'}
                  {mode === 'lengthy' && '📚 Lengthy'}
                </span>
                {deep && <span className="badge bd">🔍 Deep Research</span>}
              </div>

              {sources.length > 0 && (
                <div className="sr2">
                  {sources.map(s => (
                    <div key={s.n} className="sc2">
                      <div className="sd" style={{background: s.c}}></div>
                      {s.n}
                    </div>
                  ))}
                </div>
              )}

              <div className="rb">
                <ReactMarkdown>{report}</ReactMarkdown>
              </div>

              <div className="divlabel">Ask More</div>

              <div className="fu">
                <div className="fuhd"><MessageCircle size={14}/> Continue the research conversation</div>
                <div className="fum">
                  {chatHistory.slice(2).map((msg, i) => (
                    <div key={i} className={`fm ${msg.role === 'user' ? 'fu-u' : 'fu-a'}`}>
                      {msg.role === 'user' ? msg.content : <ReactMarkdown>{msg.content}</ReactMarkdown>}
                    </div>
                  ))}
                  {followUpLoading && (
                    <div className="fm fu-a">
                       <div className="sp" style={{width: 12, height: 12, borderWidth: 1.5}}></div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
                
                <form className="fur" onSubmit={handleFollowUp}>
                  <input 
                    className="fui" 
                    placeholder="Dig deeper… What are the limitations? What's next?"
                    value={followUp}
                    onChange={(e) => setFollowUp(e.target.value)}
                    disabled={followUpLoading}
                  />
                  <button type="submit" className="fus" disabled={followUpLoading || !followUp.trim()}>Ask →</button>
                </form>
              </div>

              <div className="ar">
                <button className="ab2 pr" onClick={downloadPDF}><Download size={14}/> Download PDF</button>
                <button className="ab2" onClick={handleCopy}><Copy size={14}/> Copy</button>
                <button className="ab2" onClick={handleNewChat}><RotateCcw size={14}/> New Search</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default App;
