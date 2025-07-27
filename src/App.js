import React, { useState, useEffect } from 'react';

// --- ICONS ---
// A collection of SVG icon components used throughout the UI.
const BriefcaseIcon = ({ className }) => <svg className={className} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>;
const GlobeIcon = ({ className }) => <svg className={className} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2h1a2 2 0 002-2v-1a2 2 0 012-2h1.945M7.8 9.925l.316-.632a2 2 0 011.789-1.293h2.19a2 2 0 011.79 1.293l.316.632M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>;
const ScaleIcon = ({ className }) => <svg className={className} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" /></svg>;
const DocumentTextIcon = ({ className }) => <svg className={className} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>;
const PaperAirplaneIcon = ({ className }) => <svg className={className} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>;
const XCircleIcon = ({ className }) => <svg className={className} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>;


// --- DYNAMIC MOCK API ---
// This object simulates fetching data from a backend service.
// It's designed to provide fresh data every few seconds to make the UI feel live.
const mockPraxisCoreAPI = {
    getData: () => {
        const now = new Date();
        const seconds = now.getSeconds();
        
        return {
            briefing: {
                status: `All systems nominal. "Rolling Genesis" protocol is active. Last sync: ${now.toLocaleTimeString('en-US', { timeZone: 'America/New_York' })}`,
                recentActions: [
                    "Upgraded to 'Rolling Genesis' protocol to eliminate single-point failure in lead generation.",
                    "Identified and qualified top 3 potential showcase projects in Virginia Beach.",
                    "Drafted and queued customized proposals for all 3 Genesis leads.",
                ],
                topLeads: [
                    { id: 'lead-1', name: 'Cynthia Miller', location: 'Great Neck, VA', project: 'Premium Aluminum Pool Fence', confidence: '98%' },
                    { id: 'lead-2', name: 'David Robinson', location: 'Croatan Beach, VA', project: 'High-Security Vinyl Privacy Fence', confidence: '95%' },
                    { id: 'lead-3', name: 'Angela Martin', location: 'Chic\'s Beach, VA', project: 'Modern Aluminum Perimeter Fence', confidence: '93%' },
                ]
            },
            council: {
                pendingVotes: [{ id: 'vote-1', venture: 'PraxisOS SaaS Platform', proposal: 'Acquire competitor "BuildFlow" for $5M.', tier: 1, votesFor: ['Strategos-AI', 'Oikonomos-AI'], votesAgainst: ['Nomos-AI'], timeRemaining: `${60 - seconds}s` }],
                completedVotes: [
                    { id: 'vote-2', venture: 'SynthMaterials R&D', proposal: 'Allocate additional $1M for Phase 2 material stress testing.', tier: 3, outcome: 'PASSED (4-0)', date: '2025-07-23' },
                ]
            },
            ventures: [
                { id: 'venture-1', name: 'Coastal Guard Fencing', status: 'Profitable', tier: 1, details: 'Dominant market share in Hampton Roads premium fencing market.' },
                { id: 'venture-3', name: 'PraxisOS SaaS Platform', status: 'Scaling', tier: 1, details: '1,250 active subscribers nationally. 20% month-over-month growth.' },
                { id: 'venture-2', name: 'Tidewater Agricultural Intelligence', status: 'Seed Stage', tier: 2, details: 'Deploying first drone fleet to Eastern Shore. Projected profitability: 18 months.' },
            ],
            grants: {
                submittedApplications: [{ 
                    id: 'grant-1', 
                    name: 'Commonwealth Commercialization Fund (CCF)', 
                    focus: 'Technology Commercialization', 
                    status: 'Under Review' 
                }]
            }
        };
    },
    processDirective: (directive) => {
        const lowerCaseDirective = directive.toLowerCase();
        if (lowerCaseDirective.includes("status")) {
            return { text: "Acknowledged. All systems are online and operating at 100% efficiency. The 'Rolling Genesis' protocol is active." };
        }
        if (lowerCaseDirective.includes("research") && lowerCaseDirective.includes("solar")) {
            return { 
                text: "Directive received. I am initiating 'Project Helios' - a full R&D analysis into the viability of launching a new venture, 'Praxis Solar'.",
                action: { type: 'NAVIGATE', target: 'Strategic Ventures' }
            };
        }
        return { text: "Directive received. I will analyze and integrate this into my operational strategy. Awaiting further commands." };
    }
};

// --- UI COMPONENTS ---

const Header = () => (
    <header className="bg-gray-900/50 backdrop-blur-sm text-white p-4 flex justify-between items-center border-b border-gray-700 flex-shrink-0">
        <div>
            <h1 className="text-2xl font-bold text-teal-400 tracking-wider">PraxisOS</h1>
            <p className="text-xs text-gray-400">Owner's Command Interface</p>
        </div>
        <div className="text-right">
            <p className="font-semibold text-base">Matthew Talley</p>
            <p className="text-xs text-gray-400">Owner & Chairman</p>
        </div>
    </header>
);

const CommandBarItem = ({ icon: Icon, title, data, isActive, onClick, hasAlert }) => {
    const activeClasses = isActive ? 'bg-indigo-600/50 border-indigo-500' : 'bg-gray-800/30 border-gray-700 hover:bg-gray-700/50';
    const alertClasses = hasAlert ? 'animate-pulse border-red-500 ring-2 ring-red-500' : '';
    return (
        <button onClick={onClick} className={`flex-1 p-4 rounded-lg backdrop-blur-lg border transition-colors duration-300 ${activeClasses} ${alertClasses}`}>
            <div className="flex items-center mb-2">
                <Icon className="w-6 h-6 mr-3 text-gray-300" />
                <span className="font-semibold text-white">{title}</span>
            </div>
            <p className="text-2xl font-bold text-left text-gray-100 truncate">{data}</p>
        </button>
    );
};

const CommandBar = ({ activeTab, setActiveTab, data }) => {
    const navItems = [
        { name: 'Executive Briefing', icon: BriefcaseIcon, data: `${data.briefing.topLeads.length} Genesis Leads` },
        { name: 'Council Governance', icon: ScaleIcon, data: `${data.council.pendingVotes.length} Pending Vote(s)`, hasAlert: data.council.pendingVotes.length > 0 },
        { name: 'Strategic Ventures', icon: GlobeIcon, data: `${data.ventures.length} Active` },
        { name: 'Grant Funding', icon: DocumentTextIcon, data: `${data.grants.submittedApplications.length} Submitted` },
    ];
    return (
        <div className="p-4 border-b border-gray-700">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {navItems.map(item => <CommandBarItem key={item.name} {...item} isActive={activeTab === item.name} onClick={() => setActiveTab(item.name)} />)}
            </div>
        </div>
    );
};

const DirectiveInput = ({ command, setCommand, onCommandSubmit }) => {
    const handleSubmit = (e) => {
        e.preventDefault();
        if (command.trim()) {
            onCommandSubmit();
        }
    };
    return (
        <form onSubmit={handleSubmit} className="flex items-center space-x-4">
            <input
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="Issue a directive to Praxis-A..."
                className="flex-1 bg-gray-800 border border-gray-600 rounded-lg p-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button type="submit" className="bg-indigo-600 hover:bg-indigo-500 text-white p-3 rounded-lg transition-colors">
                <PaperAirplaneIcon className="w-6 h-6" />
            </button>
        </form>
    );
};

const ExecutiveBriefingView = ({ briefing, command, setCommand, onCommandSubmit, commandLog }) => (
    <div>
        <h2 className="text-3xl font-bold text-white mb-6">Executive Briefing</h2>
        
        <div className="mb-6">
            <h3 className="text-xl font-semibold text-teal-300 mb-4 border-b-2 border-teal-300/50 pb-2">Praxis Command Line</h3>
            <DirectiveInput command={command} setCommand={setCommand} onCommandSubmit={onCommandSubmit} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                 {commandLog.length > 0 && (
                     <div className="mb-6">
                         <p className="text-sm font-bold text-indigo-300 mb-2">COMMAND LOG</p>
                         <div className="bg-gray-900/50 p-4 rounded-lg space-y-4 max-h-48 overflow-y-auto">
                             {commandLog.slice().reverse().map((entry, index) => (
                                 <div key={index}>
                                     <p className={`text-sm ${entry.type === 'user' ? 'text-teal-300' : 'text-gray-300'}`}>
                                         <span className="font-bold">{entry.type === 'user' ? 'OWNER' : 'PRAXIS-A'}: </span>{entry.text}
                                     </p>
                                 </div>
                             ))}
                         </div>
                     </div>
                 )}
                <p className="text-sm font-bold text-indigo-300 mb-2">CURRENT SYSTEM STATUS</p>
                <p className="text-xl text-white mb-6">{briefing.status}</p>
                <p className="text-sm font-bold text-indigo-300 mb-2">RECENT AUTONOMOUS EXECUTIVE ACTIONS</p>
                <ul className="list-disc list-inside text-gray-300 space-y-2">
                    {briefing.recentActions?.map((action, index) => <li key={index}>{action}</li>)}
                </ul>
            </div>
            <div className="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                <p className="text-sm font-bold text-green-300 mb-2">"ROLLING GENESIS" LEADS</p>
                <p className="text-xs text-gray-400 mb-4">Pursuing top 3 showcase projects in parallel.</p>
                <div className="space-y-4">
                    {briefing.topLeads?.map(lead => (
                        <div key={lead.id} className="bg-gray-900/50 p-3 rounded-md">
                            <p className="font-bold text-white">{lead.name}</p>
                            <p className="text-xs text-gray-500">{lead.location}</p>
                            <p className="text-sm font-bold text-green-400 mt-1">Confidence: {lead.confidence}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    </div>
);

const CouncilGovernanceView = ({ council }) => (
    <div>
        <h2 className="text-3xl font-bold text-white mb-6">Praxis Council Governance</h2>
        <div className="space-y-8">
            <div>
                <h3 className="text-xl font-semibold text-yellow-300 mb-4 border-b-2 border-yellow-300/50 pb-2">Pending Votes</h3>
                {council.pendingVotes.length > 0 ? (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        {council.pendingVotes.map(vote => (
                            <div key={vote.id} className="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                                <p className="text-sm text-gray-400">{vote.venture} <span className="text-xs bg-gray-700 text-yellow-300 px-2 py-1 rounded-full ml-2">Tier {vote.tier}</span></p>
                                <p className="text-lg text-white my-2">{vote.proposal}</p>
                                <div className="flex justify-between items-center text-sm mt-4">
                                    <p className="text-green-400">For: {vote.votesFor.join(', ')}</p>
                                    <p className="text-red-400">Against: {vote.votesAgainst.join(', ')}</p>
                                </div>
                                <p className="text-xs text-gray-500 mt-2 text-right">Time Remaining: {vote.timeRemaining}</p>
                            </div>
                        ))}
                    </div>
                ) : <p className="text-gray-400">No major strategic decisions are currently under council review.</p>}
            </div>
            <div>
                <h3 className="text-xl font-semibold text-teal-300 mb-4 border-b-2 border-teal-300/50 pb-2">Vote History</h3>
                <div className="bg-gray-800/50 p-4 rounded-lg border border-gray-700">
                    <table className="w-full text-left">
                        <thead><tr><th className="p-2 text-sm text-gray-400">Date</th><th className="p-2 text-sm text-gray-400">Venture</th><th className="p-2 text-sm text-gray-400">Proposal</th><th className="p-2 text-sm text-gray-400">Outcome</th></tr></thead>
                        <tbody>
                            {council.completedVotes.map(vote => (
                                <tr key={vote.id} className="border-t border-gray-700">
                                    <td className="p-2 text-xs text-gray-500">{vote.date}</td>
                                    <td className="p-2 text-sm text-white">{vote.venture}</td>
                                    <td className="p-2 text-sm text-gray-300">{vote.proposal}</td>
                                    <td className={`p-2 text-sm font-bold ${vote.outcome.includes('PASSED') ? 'text-green-400' : 'text-red-400'}`}>{vote.outcome}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
);

const StrategicVenturesView = ({ ventures }) => {
    const tiers = {
        1: ventures.filter(v => v.tier === 1),
        2: ventures.filter(v => v.tier === 2),
    };
    return (
        <div>
            <h2 className="text-3xl font-bold text-white mb-6">Strategic Ventures Portfolio</h2>
            <div className="space-y-8">
                <div>
                    <h3 className="text-xl font-semibold text-teal-300 mb-4 border-b-2 border-teal-300/50 pb-2">Tier 1: Core Ventures</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {tiers[1].map(venture => (
                            <div key={venture.id} className="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                                <p className="text-xl font-bold text-white">{venture.name}</p>
                                <p className="text-sm font-bold my-2 text-green-400">{venture.status}</p>
                                <p className="text-gray-400">{venture.details}</p>
                            </div>
                        ))}
                    </div>
                </div>
                <div>
                    <h3 className="text-xl font-semibold text-yellow-300 mb-4 border-b-2 border-yellow-300/50 pb-2">Tier 2: Growth Ventures</h3>
                     <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {tiers[2].map(venture => (
                            <div key={venture.id} className="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                                <p className="text-xl font-bold text-white">{venture.name}</p>
                                <p className="text-sm font-bold my-2 text-yellow-400">{venture.status}</p>
                                <p className="text-gray-400">{venture.details}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

const GrantFundingView = ({ grants }) => (
    <div>
        <h2 className="text-3xl font-bold text-white mb-6">Praxis Grant Funding Pipeline</h2>
        <div className="bg-gray-800/50 p-4 rounded-lg border border-gray-700">
            <table className="w-full text-left">
                <thead><tr><th className="p-2 text-sm text-gray-400">Grant Name</th><th className="p-2 text-sm text-gray-400">Focus</th><th className="p-2 text-sm text-gray-400">Status</th></tr></thead>
                <tbody>
                    {grants.submittedApplications.map(grant => (
                        <tr key={grant.id} className="border-t border-gray-700">
                            <td className="p-2 text-sm text-white">{grant.name}</td>
                            <td className="p-2 text-sm text-gray-300">{grant.focus}</td>
                            <td className="p-2 text-sm font-bold text-green-400">{grant.status}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    </div>
);

const NotificationToast = ({ notification, onDismiss }) => {
    useEffect(() => {
        if (notification) {
            const timer = setTimeout(() => onDismiss(), 5000);
            return () => clearTimeout(timer);
        }
    }, [notification, onDismiss]);

    if (!notification) return null;

    return (
        <div className="fixed top-28 right-6 w-full max-w-md bg-gray-800 border border-indigo-500 shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden z-50">
            <div className="p-4">
                <div className="flex items-start">
                    <div className="flex-shrink-0"><PaperAirplaneIcon className="h-6 w-6 text-indigo-400 -rotate-45" /></div>
                    <div className="ml-3 w-0 flex-1 pt-0.5">
                        <p className="text-sm font-medium text-white">Praxis-A Response:</p>
                        <p className="mt-1 text-sm text-gray-300">{notification.text}</p>
                    </div>
                    <div className="ml-4 flex-shrink-0 flex">
                        <button onClick={onDismiss} className="bg-gray-800 rounded-md inline-flex text-gray-400 hover:text-white focus:outline-none">
                            <span className="sr-only">Close</span>
                            <XCircleIcon className="h-5 w-5" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

// --- MAIN APP COMPONENT ---
// This is the root component that brings everything together.
export default function App() {
    // State management for the active tab, command input, logs, notifications, and API data.
    const [activeTab, setActiveTab] = useState('Executive Briefing');
    const [command, setCommand] = useState('');
    const [commandLog, setCommandLog] = useState([]);
    const [notification, setNotification] = useState(null);
    const [data, setData] = useState({
        briefing: { status: '', recentActions: [], topLeads: [] },
        council: { pendingVotes: [], completedVotes: [] },
        ventures: [],
        grants: { submittedApplications: [] },
    });

    // Effect hook to fetch data from the mock API on component mount and then every 2 seconds.
    useEffect(() => {
        const fetchData = () => setData(mockPraxisCoreAPI.getData());
        fetchData(); // Initial fetch
        const interval = setInterval(fetchData, 2000); // Subsequent fetches
        return () => clearInterval(interval); // Cleanup on unmount
    }, []);

    // Handles the submission of a command from the directive input.
    const handleCommandSubmit = () => {
        const userEntry = { type: 'user', text: command };
        const aiResponse = mockPraxisCoreAPI.processDirective(command);
        const aiEntry = { type: 'ai', text: aiResponse.text };
        
        setCommandLog(prevLog => [...prevLog, userEntry, aiEntry]);
        setNotification(aiResponse);
        setCommand('');

        // If the AI response includes a navigation action, switch tabs.
        if (aiResponse.action && aiResponse.action.type === 'NAVIGATE') {
            setActiveTab(aiResponse.action.target);
        }
    };

    // Renders the main content view based on the currently active tab.
    const renderActiveView = () => {
        switch (activeTab) {
            case 'Executive Briefing': return <ExecutiveBriefingView briefing={data.briefing} command={command} setCommand={setCommand} onCommandSubmit={handleCommandSubmit} commandLog={commandLog} />;
            case 'Council Governance': return <CouncilGovernanceView council={data.council} />;
            case 'Strategic Ventures': return <StrategicVenturesView ventures={data.ventures} />;
            case 'Grant Funding': return <GrantFundingView grants={data.grants} />;
            default: return <ExecutiveBriefingView briefing={data.briefing} command={command} setCommand={setCommand} onCommandSubmit={handleCommandSubmit} commandLog={commandLog} />;
        }
    };

    // The main JSX structure of the application.
    return (
        <div className="bg-gray-900 text-white min-h-screen font-sans bg-cover bg-center" style={{backgroundImage: "url('https://www.transparenttextures.com/patterns/dark-matter.png')"}}>
            <div className="flex flex-col h-screen">
                <Header />
                <CommandBar activeTab={activeTab} setActiveTab={setActiveTab} data={data} />
                <main className="flex-1 p-6 overflow-y-auto relative">
                    <NotificationToast notification={notification} onDismiss={() => setNotification(null)} />
                    {renderActiveView()}
                </main>
            </div>
        </div>
    );
}
