import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, NavLink, useNavigate, useParams } from "react-router-dom";
import {
  LayoutDashboard, Video, CheckSquare, Bot, BrainCircuit, Activity, Users,
  PlugZap, Settings, Search, Bell, Plus, ArrowUpRight, Clock3, Sparkles,
  MoreHorizontal, Play, FileText, CalendarDays, CheckCircle2, Circle,
  AlertCircle, Mic2, ChevronRight, Send, Menu, X, Zap, Database, ShieldCheck,
  BarChart3, Cpu, RefreshCw, UploadCloud, UserRound, SlidersHorizontal
} from "lucide-react";
import "./styles.css";
import * as api from "./api";

// Fallback mock data — used whenever the backend call fails, so the UI
// still demos even if the API isn't reachable yet.
const mockMeetings = [
  { id:"m1", title:"Product Sprint Planning", date:"Today, 10:30 AM", duration:"42 min", people:6, status:"Processed", actions:5, tone:"purple" },
  { id:"m2", title:"Frontend & MCP Integration", date:"Yesterday, 3:00 PM", duration:"31 min", people:4, status:"Processed", actions:3, tone:"blue" },
  { id:"m3", title:"Weekly Engineering Sync", date:"Aug 11, 11:00 AM", duration:"48 min", people:8, status:"Processed", actions:7, tone:"green" },
  { id:"m4", title:"Design Review", date:"Aug 9, 2:30 PM", duration:"27 min", people:5, status:"Processed", actions:2, tone:"orange" }
];

const mockTasks = [
  { id:1, title:"Build the AI Meeting Agent dashboard UI", assignee:"Rahma", due:"Today", priority:"High", status:"In Progress" },
  { id:2, title:"Connect meeting actions endpoint", assignee:"Li_do", due:"Tomorrow", priority:"High", status:"To Do" },
  { id:3, title:"Review MCP historical context retrieval", assignee:"Alex", due:"Aug 15", priority:"Medium", status:"To Do" },
  { id:4, title:"Configure Grafana observability panel", assignee:"Li_do", due:"Aug 16", priority:"Medium", status:"Done" },
  { id:5, title:"Prepare final hackathon demo", assignee:"Team", due:"Aug 17", priority:"High", status:"In Progress" }
];

// Shared hook: fetch from the API, fall back to mock data + note the failure.
// This keeps every page working today (mock) and automatically switches to
// live data the moment the backend is reachable — no code changes needed.
function useApiData(fetcher, mockData) {
  const [data, setData] = useState(mockData);
  const [loading, setLoading] = useState(true);
  const [usingMock, setUsingMock] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetcher()
      .then((res) => { if (!cancelled) { setData(res); setUsingMock(false); } })
      .catch(() => { if (!cancelled) { setData(mockData); setUsingMock(true); } })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { data, loading, usingMock };
}

function OfflineBanner({ show }) {
  if (!show) return null;
  return (
    <div className="offline-banner" style={{
      background: "#1a1a24", border: "1px solid #242431", color: "#8b8a99",
      borderRadius: 10, padding: "10px 14px", fontSize: 13, marginBottom: 16,
      display: "flex", alignItems: "center", gap: 8
    }}>
      <AlertCircle size={14} />
      Showing sample data — couldn't reach the backend. Check VITE_API_URL and that the server is running.
    </div>
  );
}

function AppShell({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { data: tasks } = useApiData(api.getTasks, mockTasks);
  const openTaskCount = tasks.filter(t => t.status !== "Done").length;
  const nav = [
    ["Dashboard","/",LayoutDashboard], ["Meetings","/meetings",Video], ["Tasks","/tasks",CheckSquare],
    ["AI Assistant","/assistant",Bot], ["MCP Memory","/memory",BrainCircuit], ["Analytics","/analytics",Activity],
    ["Team","/team",Users], ["Integrations","/integrations",PlugZap]
  ];
  return <div className="app">
    <aside className={mobileOpen ? "sidebar open" : "sidebar"}>
      <div className="brand"><div className="brand-mark"><Sparkles size={18}/></div><div><b>Meeting<span>Agent</span></b><small>AI WORKSPACE</small></div><button className="mobile-x" onClick={()=>setMobileOpen(false)}><X size={18}/></button></div>
      <div className="workspace"><div className="workspace-avatar">A</div><div><strong>Acme Workspace</strong><small>6 members</small></div><ChevronRight size={15}/></div>
      <nav>{nav.map(([label,path,Icon])=><NavLink key={path} to={path} end={path==="/"} onClick={()=>setMobileOpen(false)}><Icon size={18}/><span>{label}</span>{label==="Tasks"&&openTaskCount>0&&<em>{openTaskCount}</em>}</NavLink>)}</nav>
      <div className="nav-bottom">
        <NavLink to="/settings"><Settings size={18}/><span>Settings</span></NavLink>
        <div className="agent-status"><span className="pulse"></span><div><b>Agent online</b><small>All systems operational</small></div></div>
        <div className="user"><div className="avatar">R</div><div><b>Rahma</b><small>Engineer</small></div><MoreHorizontal size={17}/></div>
      </div>
    </aside>
    {mobileOpen && <div className="overlay" onClick={()=>setMobileOpen(false)} />}
    <main className="main">
      <header className="topbar"><button className="hamburger" onClick={()=>setMobileOpen(true)}><Menu/></button><div className="search"><Search size={17}/><input placeholder="Search meetings, tasks, people..." /></div><div className="top-actions"><button className="icon-btn"><Bell size={18}/><i></i></button><button className="top-avatar">R</button></div></header>
      <div className="content">{children}</div>
    </main>
  </div>
}

function PageTitle({eyebrow,title,description,action, onAction}) {
  return <div className="page-title"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{description&&<p>{description}</p>}</div>{action&&<button className="primary" onClick={onAction}>{action}</button>}</div>
}

function Stat({icon:Icon,label,value,change,negative}) {
  return <div className="stat"><div className="stat-top"><div className="stat-icon"><Icon size={18}/></div><span className={negative?"change negative":"change"}>{change}</span></div><strong>{value}</strong><span>{label}</span></div>
}

function Dashboard(){
 const nav=useNavigate();
 const { data: meetings, loading: meetingsLoading, usingMock: meetingsMock } = useApiData(api.getMeetings, mockMeetings);
 const { data: tasks, usingMock: tasksMock } = useApiData(api.getTasks, mockTasks);
 return <><PageTitle eyebrow="WORKSPACE OVERVIEW" title="Good morning, Rahma." description="Your meetings are turning into actions. Here's what needs your attention." action="New meeting" onAction={()=>nav("/meetings/new")}/>
 <OfflineBanner show={meetingsMock || tasksMock} />
 <div className="hero-card"><div className="hero-copy"><div className="mini-pill"><Sparkles size={13}/> AI agent active</div><h2>Turn every meeting into momentum.</h2><p>MeetingAgent listens, understands decisions, remembers context and turns conversations into accountable work.</p><div className="hero-buttons"><button className="primary" onClick={()=>nav("/meetings/new")}><Plus size={16}/> Start a meeting</button><button className="ghost" onClick={()=>nav("/assistant")}><Bot size={16}/> Ask your agent</button></div></div><div className="hero-orb"><div className="orb-core"><Sparkles size={28}/></div><span className="orb-line l1"></span><span className="orb-line l2"></span><span className="orb-line l3"></span><div className="orb-chip c1">MCP</div><div className="orb-chip c2">Gemini</div><div className="orb-chip c3">Actions</div></div></div>
 <div className="stats"><Stat icon={Video} value="18" label="Meetings this month" change="+12%"/><Stat icon={CheckSquare} value="47" label="Actions extracted" change="+24%"/><Stat icon={Clock3} value="8.4h" label="Time saved" change="+31%"/><Stat icon={AlertCircle} value="5" label="Tasks need attention" change="2 overdue" negative/></div>
 <div className="grid-2"><section className="panel"><div className="panel-head"><div><h3>Recent meetings</h3><p>Latest processed conversations</p></div><button className="link-btn" onClick={()=>nav("/meetings")}>View all <ArrowUpRight size={15}/></button></div><div className="meeting-list">{meetingsLoading?<p className="muted">Loading meetings…</p>:meetings.slice(0,3).map(m=><MeetingRow key={m.id} m={m} onClick={()=>nav("/meetings/"+m.id)}/>)}</div></section>
 <section className="panel"><div className="panel-head"><div><h3>Action items</h3><p>Prioritized by your AI agent</p></div><button className="link-btn" onClick={()=>nav("/tasks")}>All tasks <ArrowUpRight size={15}/></button></div><div className="task-list">{tasks.slice(0,4).map(t=><TaskRow key={t.id} t={t}/>)}</div></section></div>
 <div className="grid-3"><Insight title="Decision velocity" value="86%" text="of decisions from your last 10 meetings have an owner."/><Insight title="Context retrieval" value="94%" text="MCP retrieved relevant historical context."/><Insight title="Agent confidence" value="91%" text="average confidence for extracted actions."/></div>
 </>;
}
function MeetingRow({m,onClick}){return <button className="meeting-row" onClick={onClick}><div className={"meeting-icon "+m.tone}><Video size={18}/></div><div className="row-main"><b>{m.title}</b><span>{m.date} · {m.duration} · {m.people} participants</span></div><div className="row-meta"><span className="status-dot"></span><small>{m.actions} actions</small><ChevronRight size={16}/></div></button>}
function TaskRow({t}){return <div className="task-row"><div className={t.status==="Done"?"task-check done":"task-check"}>{t.status==="Done"?<CheckCircle2 size={17}/>:<Circle size={17}/>}</div><div className="row-main"><b>{t.title}</b><span>{t.assignee} · Due {t.due}</span></div><span className={"priority "+t.priority.toLowerCase()}>{t.priority}</span></div>}
function Insight({title,value,text}){return <div className="insight"><div className="insight-icon"><Sparkles size={16}/></div><div><span>{title}</span><strong>{value}</strong><p>{text}</p></div></div>}

function Meetings(){
 const nav=useNavigate();
 const { data: meetings, loading, usingMock } = useApiData(api.getMeetings, mockMeetings);
 return <><PageTitle eyebrow="KNOWLEDGE BASE" title="Meetings" description="Every conversation, transcript and AI-generated outcome in one place." action="New meeting" onAction={()=>nav("/meetings/new")}/>
 <OfflineBanner show={usingMock} />
 <div className="toolbar"><div className="search large"><Search size={17}/><input placeholder="Search meetings..." /></div><button className="filter"><CalendarDays size={16}/> Date <ChevronRight size={15}/></button><button className="filter"><SlidersHorizontal size={16}/> Filters</button></div>
 {loading?<p className="muted">Loading meetings…</p>:
 <div className="meeting-grid">{meetings.map(m=><div className="meeting-card" key={m.id} onClick={()=>nav("/meetings/"+m.id)}><div className={"card-cover "+m.tone}><div className="wave"><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div><button className="play"><Play size={15} fill="currentColor"/></button></div><div className="card-body"><div className="card-kicker">{m.status}<span>•</span>{m.duration}</div><h3>{m.title}</h3><p>{m.date} · {m.people} participants</p><div className="card-footer"><span><CheckSquare size={14}/> {m.actions} actions</span><span className="mini-avatars"><i>R</i><i>A</i><i>L</i></span></div></div></div>)}</div>}
 </>
}

// FIX: this previously always showed the hardcoded "Product Sprint Planning"
// meeting regardless of which meeting was clicked, and listed *all* tasks
// instead of that meeting's tasks. Now it reads the :id param, fetches
// (or looks up) the right meeting, and falls back to mock only if needed.
function MeetingDetails(){
 const nav=useNavigate();
 const { id } = useParams();
 const [meeting, setMeeting] = useState(null);
 const [meetingLoading, setMeetingLoading] = useState(true);
 const [usingMock, setUsingMock] = useState(false);
 const { data: allTasks } = useApiData(api.getTasks, mockTasks);

 useEffect(() => {
   let cancelled = false;
   setMeetingLoading(true);
   api.getMeeting(id)
     .then((res) => { if (!cancelled) { setMeeting(res); setUsingMock(false); } })
     .catch(() => {
       if (!cancelled) {
         setMeeting(mockMeetings.find(m => m.id === id) || mockMeetings[0]);
         setUsingMock(true);
       }
     })
     .finally(() => { if (!cancelled) setMeetingLoading(false); });
   return () => { cancelled = true; };
 }, [id]);

 // TODO: once the backend confirms the shape, filter tasks by meeting id
 // (e.g. t.meeting_id === id) instead of showing every task.
 const meetingTasks = allTasks;

 if (meetingLoading) return <p className="muted">Loading meeting…</p>;
 if (!meeting) return <p className="muted">Meeting not found.</p>;

 return <><div className="back" onClick={()=>nav("/meetings")}><ChevronRight size={15} style={{transform:"rotate(180deg)"}}/> Back to meetings</div>
 <OfflineBanner show={usingMock} />
 <div className="detail-head"><div><div className="eyebrow">MEETING · {(meeting.date||"").toUpperCase()}</div><h1>{meeting.title}</h1><p><Users size={15}/> {meeting.people} participants · {meeting.duration} · {meeting.status}</p></div><button className="primary"><DownloadIcon/> Export report</button></div>
 <div className="detail-layout"><div><section className="panel"><div className="panel-head"><div><h3>AI summary</h3><p>Generated by Gemini · 91% confidence</p></div><span className="ai-badge"><Sparkles size={13}/> AI generated</span></div><div className="summary"><p>The team aligned on the MVP launch scope and agreed to prioritize the meeting action workflow. Frontend work starts with the dashboard and meeting detail views, while the backend team finalizes the actions API and MCP context retrieval.</p><div className="summary-points"><div><CheckCircle2 size={16}/><span><b>Decision:</b> Ship the action extraction workflow in the first demo.</span></div><div><CheckCircle2 size={16}/><span><b>Decision:</b> Use MCP memory to surface relevant previous decisions.</span></div><div><CheckCircle2 size={16}/><span><b>Risk:</b> Validate AI confidence before automatically assigning tasks.</span></div></div></div></section>
 <section className="panel"><div className="panel-head"><div><h3>Action items <span className="count">{meetingTasks.length}</span></h3><p>Review and confirm what the agent extracted.</p></div><button className="ghost"><Plus size={15}/> Add action</button></div><div className="action-table">{meetingTasks.map((t,i)=><div className="action-item" key={t.id}><div className="action-number">{i+1}</div><div className="action-main"><b>{t.title}</b><span><UserRound size={13}/> {t.assignee} <i>·</i> <CalendarDays size={13}/> {t.due}</span></div><span className="confidence"><span></span>{95-i*3}%</span><button className="more"><MoreHorizontal size={17}/></button></div>)}</div></section></div>
 <aside className="detail-side"><section className="panel"><div className="panel-head"><h3>Meeting context</h3></div><div className="context-list"><div><span>Participants</span><b>{meeting.people} people</b></div><div><span>Duration</span><b>{meeting.duration}</b></div><div><span>Language</span><b>English</b></div><div><span>AI model</span><b>Gemini</b></div><div><span>Memory</span><b className="green-text">MCP connected</b></div></div></section><section className="panel"><div className="panel-head"><h3>Related context</h3></div><div className="memory-card"><div className="memory-icon"><BrainCircuit size={16}/></div><div><b>Frontend & MCP Integration</b><span>Yesterday · 3 decisions</span></div><ChevronRight size={15}/></div><div className="memory-card"><div className="memory-icon"><Database size={16}/></div><div><b>MVP scope discussion</b><span>Aug 8 · 2 decisions</span></div><ChevronRight size={15}/></div></section></aside></div></>
}
function DownloadIcon(){return <FileText size={16}/>}

function NewMeeting(){
 const [started,setStarted]=useState(false);
 return <><PageTitle eyebrow="NEW MEETING" title={started?"Agent is listening":"Start a new meeting"} description={started?"Your agent is capturing context and will extract actions automatically.":"Record a conversation, upload a recording, or paste a transcript."}/><div className="new-meeting"><div className={started?"record-card recording":"record-card"}><div className="record-orb">{started?<><span className="rec-ring"></span><Mic2 size={35}/></>:<Mic2 size={35}/>}</div><h2>{started?"Meeting in progress":"Ready when you are"}</h2><p>{started?"AI transcription is active. You can stop anytime.":"MeetingAgent will transcribe, summarize and extract accountable actions."}</p>{started?<button className="danger" onClick={()=>setStarted(false)}>Stop meeting</button>:<button className="primary big" onClick={()=>setStarted(true)}><Mic2 size={17}/> Start recording</button>}</div><div className="upload-card"><div className="upload-icon"><UploadCloud size={24}/></div><h3>Upload a recording</h3><p>MP3, WAV, M4A or MP4 up to 500MB</p><button className="ghost">Choose file</button><div className="divider"><span>or</span></div><button className="transcript"><FileText size={16}/> Paste a transcript</button></div></div></>
}

function Tasks(){
 const { data: tasks, loading, usingMock } = useApiData(api.getTasks, mockTasks);
 return <><PageTitle eyebrow="WORK MANAGEMENT" title="Tasks" description="Action items extracted from your meetings, organized by ownership and status." action="Add task"/>
 <OfflineBanner show={usingMock} />
 <div className="task-stats"><div><span>Open</span><b>{tasks.filter(t=>t.status==="To Do").length}</b></div><div><span>In progress</span><b>{tasks.filter(t=>t.status==="In Progress").length}</b></div><div><span>Completed</span><b>{tasks.filter(t=>t.status==="Done").length}</b></div><div><span>Overdue</span><b className="red-text">1</b></div></div>
 {loading?<p className="muted">Loading tasks…</p>:
 <div className="kanban">{["To Do","In Progress","Done"].map(status=><div className="kanban-col" key={status}><div className="kanban-head"><h3>{status}</h3><span>{tasks.filter(t=>t.status===status).length}</span><Plus size={16}/></div>{tasks.filter(t=>t.status===status).map(t=><div className="kanban-card" key={t.id}><div className="kc-top"><span className={"priority "+t.priority.toLowerCase()}>{t.priority}</span><MoreHorizontal size={16}/></div><h4>{t.title}</h4><div className="kc-meta"><span className="person">{t.assignee[0]}</span><span><CalendarDays size={13}/> {t.due}</span></div></div>)}</div>)}</div>}
 </>
}

function Assistant(){
 const [messages,setMessages]=useState([{role:"ai",text:"Hi Rahma. I have access to your meeting history and current action items. What would you like to know?"}]);
 const [input,setInput]=useState("");
 const [sending,setSending]=useState(false);
 const send=async ()=>{
   if(!input.trim()||sending)return;
   const q=input;
   setMessages(m=>[...m,{role:"user",text:q}]);
   setInput("");
   setSending(true);
   try{
     const res = await api.askAssistant(q);
     setMessages(m=>[...m,{role:"ai",text: res?.reply || res?.message || "Got a response from the agent."}]);
   }catch{
     // Fallback: keep the UI usable even if /assistant isn't live yet.
     setMessages(m=>[...m,{role:"ai",text:"Based on your recent meetings, I found relevant context. The action extraction workflow is the highest-priority item for the MVP. I can show the related decisions and owners if you'd like. (offline demo reply — /assistant endpoint not reachable)"}]);
   }finally{
     setSending(false);
   }
 };
 return <><PageTitle eyebrow="AGENTIC AI" title="AI Assistant" description="Ask questions across your meetings, tasks and team memory."/><div className="assistant-layout"><div className="chat"><div className="chat-head"><div className="ai-avatar"><Sparkles size={18}/></div><div><b>MeetingAgent</b><span>Connected to Gemini + MCP memory</span></div><span className="online"><i/> Online</span></div><div className="messages">{messages.map((m,i)=><div className={m.role==="ai"?"message ai":"message user"} key={i}><div className="message-avatar">{m.role==="ai"?<Sparkles size={14}/>: "R"}</div><div className="bubble">{m.text}</div></div>)}{sending&&<div className="message ai"><div className="message-avatar"><Sparkles size={14}/></div><div className="bubble">Thinking…</div></div>}</div><div className="suggestions">{["Who owns the frontend work?","What did we decide yesterday?","Show overdue actions"].map(s=><button key={s} onClick={()=>setInput(s)}>{s}</button>)}</div><div className="composer"><input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()} placeholder="Ask anything about your meetings..." /><button onClick={send}><Send size={17}/></button></div></div><aside className="assistant-side"><div className="panel"><div className="panel-head"><h3>Agent capabilities</h3></div>{[["Meeting search",Search],["Action extraction",CheckSquare],["MCP memory",BrainCircuit],["Team context",Users]].map(([x,I])=><div className="capability" key={x}><div><I size={16}/></div><span>{x}</span><CheckCircle2 size={15}/></div>)}</div><div className="panel"><div className="panel-head"><h3>Recent context</h3></div><p className="muted">The agent used 4 relevant sources for your last question.</p><div className="source"><BrainCircuit size={15}/><span>Frontend & MCP Integration</span></div><div className="source"><Video size={15}/><span>Product Sprint Planning</span></div></div></aside></div></>
}

function Memory(){
 return <><PageTitle eyebrow="LONG-TERM CONTEXT" title="MCP Memory" description="Historical context retrieved by the agent so decisions don't get lost." action="Refresh memory"/><div className="memory-overview"><div className="memory-big"><div className="memory-network"><div className="node center"><BrainCircuit size={23}/></div><div className="node n1">MCP</div><div className="node n2">Decisions</div><div className="node n3">Tasks</div><div className="node n4">Meetings</div></div><div><span>Connected memory</span><strong>1,284</strong><p>context records available to your agent</p></div></div><div className="memory-metrics"><div><Database size={17}/><span>Sources</span><b>24</b></div><div><RefreshCw size={17}/><span>Last sync</span><b>2m ago</b></div><div><ShieldCheck size={17}/><span>Retrieval accuracy</span><b>94%</b></div></div></div><div className="grid-2"><section className="panel"><div className="panel-head"><div><h3>Recent retrieved context</h3><p>What your agent has been using</p></div></div>{["Frontend & MCP Integration","Product Sprint Planning","MVP scope discussion","Weekly Engineering Sync"].map((x,i)=><div className="memory-row" key={x}><div className="memory-icon"><BrainCircuit size={16}/></div><div><b>{x}</b><span>{i+2} relevant memories · Retrieved today</span></div><span className="match">{96-i*4}% match</span></div>)}</section><section className="panel"><div className="panel-head"><div><h3>Memory categories</h3><p>Indexed workspace knowledge</p></div></div>{[["Decisions","324"],["Action items","286"],["Meeting summaries","418"],["Team context","156"],["Other","100"]].map(x=><div className="bar-row" key={x[0]}><span>{x[0]}</span><b>{x[1]}</b><div><i style={{width:(parseInt(x[1])/418*100)+"%"}}></i></div></div>)}</section></div></>
}

function Analytics(){
 return <><PageTitle eyebrow="OBSERVABILITY" title="Agent Analytics" description="Monitor the health, quality and performance of your AI meeting agent." action="Open Grafana"/><div className="stats"><Stat icon={Zap} value="98.7%" label="Agent success rate" change="+1.4%"/><Stat icon={Cpu} value="2.8s" label="Avg. processing time" change="-18%"/><Stat icon={Database} value="94%" label="MCP retrieval accuracy" change="+6%"/><Stat icon={BarChart3} value="91%" label="Action confidence" change="+4%"/></div><div className="analytics-grid"><section className="panel chart-panel"><div className="panel-head"><div><h3>Agent executions</h3><p>Successful vs failed runs · Last 7 days</p></div><span className="legend"><i/> Executions</span></div><div className="chart"><div className="ylabels"><span>800</span><span>600</span><span>400</span><span>200</span><span>0</span></div><div className="chart-area">{[42,58,49,72,66,88,78].map((h,i)=><div className="bar" style={{height:h+"%"}} key={i}><i></i><span>{["Thu","Fri","Sat","Sun","Mon","Tue","Wed"][i]}</span></div>)}</div></div></section><section className="panel"><div className="panel-head"><div><h3>Pipeline health</h3><p>Live agent components</p></div></div>{[["Gemini API","Operational","99.9%",Sparkles],["FastAPI backend","Operational","100%",Cpu],["MCP server","Operational","98.7%",BrainCircuit],["Grafana","Operational","99.8%",Activity]].map(([x,s,p,I])=><div className="health" key={x}><div className="health-icon"><I size={16}/></div><div><b>{x}</b><span><i/> {s}</span></div><strong>{p}</strong></div>)}</section></div><div className="panel"><div className="panel-head"><div><h3>Recent agent events</h3><p>Latest processing activity</p></div></div><div className="events">{["Action extraction completed","MCP retrieved 6 relevant memories","Meeting transcription completed","Grafana health check passed"].map((x,i)=><div className="event" key={x}><span className="event-dot"></span><div><b>{x}</b><span>{i+1} minute{i?"s":""} ago · Product Sprint Planning</span></div><span className="success">Success</span></div>)}</div></div></>
}

function Generic({type}){
 const data={Team:["Team","Manage members and ownership across your workspace.",Users],Integrations:["Integrations","Connect Gemini, MCP, Grafana and your team tools.",PlugZap],Settings:["Settings","Configure your workspace, agent and notifications.",Settings]}[type];
 const I=data[2];
 return <><PageTitle eyebrow="WORKSPACE" title={data[0]} description={data[1]}/><div className="settings-grid"><section className="panel settings-main"><div className="settings-hero"><div className="large-setting-icon"><I size={25}/></div><div><h2>{type==="Team"?"Your team":"MeetingAgent configuration"}</h2><p>Everything you need to keep the workspace connected and ready for the next meeting.</p></div></div>{["AI processing","MCP context memory","Real-time observability","Meeting notifications"].map((x,i)=><div className="setting-row" key={x}><div><b>{x}</b><span>{i===0?"Gemini handles transcription, summaries and action extraction.":"Connected and operating normally."}</span></div><div className="toggle on"><i/></div></div>)}</section><aside className="panel"><div className="panel-head"><h3>System status</h3></div><div className="system-status"><div className="status-icon"><CheckCircle2/></div><b>Everything looks good</b><p>All core MeetingAgent services are connected.</p></div></aside></div></>
}

function App(){return <AppShell><Routes><Route path="/" element={<Dashboard/>}/><Route path="/meetings" element={<Meetings/>}/><Route path="/meetings/new" element={<NewMeeting/>}/><Route path="/meetings/:id" element={<MeetingDetails/>}/><Route path="/tasks" element={<Tasks/>}/><Route path="/assistant" element={<Assistant/>}/><Route path="/memory" element={<Memory/>}/><Route path="/analytics" element={<Analytics/>}/><Route path="/team" element={<Generic type="Team"/>}/><Route path="/integrations" element={<Generic type="Integrations"/>}/><Route path="/settings" element={<Generic type="Settings"/>}/></Routes></AppShell>}

createRoot(document.getElementById("root")).render(<BrowserRouter><App/></BrowserRouter>);
