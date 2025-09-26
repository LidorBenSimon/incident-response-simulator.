const { useState, useEffect } = React;

const Dashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [selectedAction, setSelectedAction] = useState('');
  const [responseTime, setResponseTime] = useState(0);
  const [scenarioActive, setScenarioActive] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scenarioId, setScenarioId] = useState(null);

  // פונקציה לטעינת נתונים מהAPI
  const fetchAlerts = async () => {
    try {
      // בדיקה אם יש תרחיש פעיל
      const scenariosResponse = await fetch('http://localhost:8000/scenarios');
      const scenariosData = await scenariosResponse.json();
      
      if (scenariosData.active_scenarios > 0) {
        setScenarioActive(true);
        setScenarioId(1); // נניח שזה תרחיש 1
        
        // קבלת הלוגים מהתרחיש
        const statusResponse = await fetch('http://localhost:8000/scenarios/1/status');
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          
          // המרת הלוגים לפורמט התרעות
          const apiAlerts = statusData.logs.map((log, index) => ({
            id: index + 1,
            timestamp: log.timestamp,
            level: log.level === 'WARNING' ? 'WARNING' : log.level === 'ERROR' ? 'CRITICAL' : 'INFO',
            message: log.message,
            source: log.source || 'System'
          }));
          
          setAlerts(apiAlerts);
        }
      } else {
        // אם אין תרחיש פעיל, נשתמש בהתרעות דמה
        setAlerts([
          {
            id: 1,
            timestamp: new Date().toISOString(),
            level: 'INFO',
            message: 'System initialized - No active scenarios',
            source: 'IR Simulator'
          }
        ]);
      }
    } catch (error) {
      console.error('Error fetching alerts:', error);
      // במקרה של שגיאה, נשתמש בהתרעות דמה
      setAlerts([
        {
          id: 1,
          timestamp: new Date().toISOString(),
          level: 'WARNING',
          message: 'Failed to connect to monitoring system',
          source: 'System Alert'
        }
      ]);
    }
  };

  // פונקציה להתחלת תרחיש
  const startScenario = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/scenarios/1/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setScenarioId(1);
        setScenarioActive(true);
        setResponseTime(0);
        
        // המתנה קצרה ואז טעינת התרעות
        setTimeout(() => {
          fetchAlerts();
        }, 2000);
      }
    } catch (error) {
      console.error('Error starting scenario:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    
    // ספירת זמן תגובה רק אם התרחיש פעיל
    let timer;
    if (scenarioActive && !selectedAction) {
      timer = setInterval(() => {
        setResponseTime(prev => prev + 1);
      }, 1000);
    }

    return () => {
      if (timer) clearInterval(timer);
    };
  }, [scenarioActive, selectedAction]);

  const handleResponse = async (action) => {
    if (!scenarioActive || !scenarioId) return;
    
    setSelectedAction(action);
    setLoading(true);
    
    try {
      const response = await fetch(`http://localhost:8000/scenarios/${scenarioId}/response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action: action,
          response_time: responseTime
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setFeedback(data.evaluation);
        
        // אם התרחיש הושלם, עצור אותו
        if (data.scenario_status === 'completed') {
          setScenarioActive(false);
        }
      } else {
        setFeedback({
          is_correct: false,
          score: 0,
          feedback: ['Failed to submit response. Please try again.'],
          recommendations: []
        });
      }
    } catch (error) {
      console.error('Error submitting response:', error);
      setFeedback({
        is_correct: false,
        score: 0,
        feedback: ['Network error. Please check connection.'],
        recommendations: []
      });
    } finally {
      setLoading(false);
    }
  };

  const resetScenario = () => {
    setSelectedAction('');
    setFeedback(null);
    setResponseTime(0);
    setScenarioActive(false);
    setScenarioId(null);
  };

  const getAlertIcon = (level) => {
    switch (level) {
      case 'CRITICAL': return '🚨';
      case 'WARNING': return '⚠️';
      default: return 'ℹ️';
    }
  };

  const getAlertColor = (level) => {
    switch (level) {
      case 'CRITICAL': return 'border-red-500 bg-red-50';
      case 'WARNING': return 'border-yellow-500 bg-yellow-50';
      default: return 'border-blue-500 bg-blue-50';
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return React.createElement('div', { className: 'min-h-screen bg-gray-100 p-6' },
    React.createElement('div', { className: 'max-w-6xl mx-auto' },
      
      // Header
      React.createElement('div', { className: 'bg-white rounded-lg shadow-md p-6 mb-6' },
        React.createElement('div', { className: 'flex items-center justify-between' },
          React.createElement('h1', { className: 'text-2xl font-bold text-gray-800' },
            'Incident Response Training Dashboard'
          ),
          React.createElement('div', { className: 'flex items-center space-x-4' },
            scenarioActive && React.createElement('div', { className: 'flex items-center text-gray-600' },
              React.createElement('span', null, `⏱️ Response Time: ${formatTime(responseTime)}`)
            ),
            React.createElement('div', { 
              className: `px-3 py-1 rounded-full text-sm font-medium ${
                scenarioActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }` 
            }, scenarioActive ? 'Scenario Active' : 'No Active Scenario'),
            !scenarioActive && React.createElement('button', {
              onClick: startScenario,
              disabled: loading,
              className: 'px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50'
            }, loading ? 'Starting...' : 'Start Scenario')
          )
        )
      ),

      React.createElement('div', { className: 'grid grid-cols-1 lg:grid-cols-3 gap-6' },
        
        // Alerts Feed
        React.createElement('div', { className: 'lg:col-span-2' },
          React.createElement('div', { className: 'bg-white rounded-lg shadow-md p-6' },
            React.createElement('h2', { className: 'text-xl font-semibold text-gray-800 mb-4' },
              'Security Alerts Feed'
            ),
            React.createElement('div', { className: 'space-y-3 max-h-96 overflow-y-auto' },
              alerts.map(alert =>
                React.createElement('div', {
                  key: alert.id,
                  className: `p-4 border-l-4 rounded-r-lg ${getAlertColor(alert.level)}`
                },
                  React.createElement('div', { className: 'flex items-start justify-between' },
                    React.createElement('div', { className: 'flex items-start space-x-3' },
                      React.createElement('span', { className: 'text-lg' }, getAlertIcon(alert.level)),
                      React.createElement('div', null,
                        React.createElement('p', { className: 'text-sm font-medium text-gray-800' },
                          alert.message
                        ),
                        React.createElement('p', { className: 'text-xs text-gray-500 mt-1' },
                          `${alert.source} • ${new Date(alert.timestamp).toLocaleTimeString()}`
                        )
                      )
                    ),
                    React.createElement('span', {
                      className: `px-2 py-1 text-xs rounded font-medium ${
                        alert.level === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                        alert.level === 'WARNING' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`
                    }, alert.level)
                  )
                )
              )
            )
          )
        ),

        // Response Actions & Feedback
        React.createElement('div', { className: 'space-y-6' },
          
          // Actions Panel
          !feedback && React.createElement('div', { className: 'bg-white rounded-lg shadow-md p-6' },
            React.createElement('h3', { className: 'text-lg font-semibold text-gray-800 mb-4' },
              'Incident Response Actions'
            ),
            React.createElement('div', { className: 'space-y-3' },
              
              React.createElement('button', {
                onClick: () => handleResponse('monitor'),
                disabled: !scenarioActive || loading,
                className: `w-full p-3 text-left rounded-lg border-2 transition-colors disabled:opacity-50 ${
                  selectedAction === 'monitor' ? 
                  'border-blue-500 bg-blue-50' : 
                  'border-gray-200 hover:border-gray-300'
                }`
              },
                React.createElement('div', { className: 'font-medium' }, 'Continue Monitoring'),
                React.createElement('div', { className: 'text-sm text-gray-600' },
                  'Increase logging and watch for additional indicators'
                )
              ),

              React.createElement('button', {
                onClick: () => handleResponse('isolate'),
                disabled: !scenarioActive || loading,
                className: `w-full p-3 text-left rounded-lg border-2 transition-colors disabled:opacity-50 ${
                  selectedAction === 'isolate' ? 
                  'border-yellow-500 bg-yellow-50' : 
                  'border-gray-200 hover:border-gray-300'
                }`
              },
                React.createElement('div', { className: 'font-medium' }, 'Isolate Affected System'),
                React.createElement('div', { className: 'text-sm text-gray-600' },
                  'Disconnect DESKTOP-VICTIM01 from network'
                )
              ),

              React.createElement('button', {
                onClick: () => handleResponse('block_ip'),
                disabled: !scenarioActive || loading,
                className: `w-full p-3 text-left rounded-lg border-2 transition-colors disabled:opacity-50 ${
                  selectedAction === 'block_ip' ? 
                  'border-orange-500 bg-orange-50' : 
                  'border-gray-200 hover:border-gray-300'
                }`
              },
                React.createElement('div', { className: 'font-medium' }, 'Block Malicious IP'),
                React.createElement('div', { className: 'text-sm text-gray-600' },
                  'Add evil-bank.com to firewall blocklist'
                )
              ),

              React.createElement('button', {
                onClick: () => handleResponse('escalate'),
                disabled: !scenarioActive || loading,
                className: `w-full p-3 text-left rounded-lg border-2 transition-colors disabled:opacity-50 ${
                  selectedAction === 'escalate' ? 
                  'border-red-500 bg-red-50' : 
                  'border-gray-200 hover:border-gray-300'
                }`
              },
                React.createElement('div', { className: 'font-medium' }, 'Escalate to Security Team'),
                React.createElement('div', { className: 'text-sm text-gray-600' },
                  'Alert senior security analysts immediately'
                )
              )
            )
          ),

          // Feedback Panel
          feedback && React.createElement('div', { className: 'bg-white rounded-lg shadow-md p-6' },
            React.createElement('h3', { className: 'text-lg font-semibold text-gray-800 mb-4' },
              'Performance Feedback'
            ),
            React.createElement('div', { className: 'space-y-4' },
              
              // Score
              React.createElement('div', { className: 'text-center p-4 bg-gray-50 rounded-lg' },
                React.createElement('div', { className: 'text-3xl font-bold text-blue-600' },
                  `${feedback.score}/${feedback.max_score}`
                ),
                React.createElement('div', { className: 'text-sm text-gray-600' }, 'Score'),
                React.createElement('div', { 
                  className: `inline-block px-3 py-1 rounded-full text-sm font-medium mt-2 ${
                    feedback.is_correct ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
                  }`
                }, feedback.is_correct ? 'Correct Response' : 'Needs Improvement')
              ),

              // Feedback
              React.createElement('div', null,
                React.createElement('h4', { className: 'font-medium text-gray-800 mb-2' }, 'Feedback:'),
                React.createElement('ul', { className: 'space-y-1' },
                  feedback.feedback.map((item, index) =>
                    React.createElement('li', { key: index, className: 'text-sm text-gray-600' },
                      `• ${item}`
                    )
                  )
                )
              ),

              // Recommendations
              feedback.recommendations.length > 0 && React.createElement('div', null,
                React.createElement('h4', { className: 'font-medium text-gray-800 mb-2' }, 'Recommendations:'),
                React.createElement('ul', { className: 'space-y-1' },
                  feedback.recommendations.map((item, index) =>
                    React.createElement('li', { key: index, className: 'text-sm text-blue-600' },
                      `• ${item}`
                    )
                  )
                )
              ),

              React.createElement('button', {
                onClick: resetScenario,
                className: 'w-full mt-4 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors'
              }, 'Try Another Scenario')
            )
          ),

          // Scenario Info
          React.createElement('div', { className: 'bg-white rounded-lg shadow-md p-6' },
            React.createElement('h3', { className: 'text-lg font-semibold text-gray-800 mb-4' },
              'Current Scenario'
            ),
            React.createElement('div', { className: 'space-y-2' },
              React.createElement('div', { className: 'flex justify-between' },
                React.createElement('span', { className: 'text-sm text-gray-600' }, 'Type:'),
                React.createElement('span', { className: 'text-sm font-medium' }, 'Phishing Attack')
              ),
              React.createElement('div', { className: 'flex justify-between' },
                React.createElement('span', { className: 'text-sm text-gray-600' }, 'Difficulty:'),
                React.createElement('span', { className: 'text-sm font-medium' }, 'Beginner')
              ),
              React.createElement('div', { className: 'flex justify-between' },
                React.createElement('span', { className: 'text-sm text-gray-600' }, 'Status:'),
                React.createElement('span', { 
                  className: `text-sm font-medium ${
                    scenarioActive ? 'text-green-600' : 'text-gray-600'
                  }`
                }, scenarioActive ? 'Active' : 'Inactive')
              )
            )
          )
        )
      )
    )
  );
};

// רינדור הקומפוננטה
ReactDOM.render(React.createElement(Dashboard), document.getElementById('root'));
