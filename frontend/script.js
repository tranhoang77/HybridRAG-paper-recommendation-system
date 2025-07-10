// script.js

const API_BASE_URL = 'http://localhost:8777'; 
let currentUser = null;

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
}

function showLogin() { showPage('loginPage'); }
function showRegister() { showPage('registerPage'); }
function showDashboard() { 
    showPage('dashboardPage');
    loadTopics();
}
function showAddTopic() { showPage('addTopicPage'); }

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    if (data) {
        options.body = JSON.stringify(data);
    }
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    return response;
}


document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    try {
        const response = await apiCall('/register', 'POST', { email, password });
        const result = await response.json();
        if (response.ok) {
            document.getElementById('registerSuccess').style.display = 'block';
            document.getElementById('registerSuccess').textContent = 'Registration successful! You can now login.';
            document.getElementById('registerError').style.display = 'none';
            document.getElementById('registerForm').reset();
        } else {
            document.getElementById('registerError').style.display = 'block';
            document.getElementById('registerError').textContent = result.detail || 'Registration failed';
            document.getElementById('registerSuccess').style.display = 'none';
        }
    } catch (error) {
        document.getElementById('registerError').style.display = 'block';
        document.getElementById('registerError').textContent = 'Network error. Please try again.';
    }
});

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    try {
        const response = await apiCall('/login', 'POST', { email, password });
        const result = await response.json();
        if (response.ok) {
            currentUser = email;
            document.getElementById('userEmail').textContent = email;
            showDashboard();
            document.getElementById('loginError').style.display = 'none';
        } else {
            document.getElementById('loginError').style.display = 'block';
            document.getElementById('loginError').textContent = result.detail || 'Login failed';
        }
    } catch (error) {
        document.getElementById('loginError').style.display = 'block';
        document.getElementById('loginError').textContent = 'Network error. Please try again.';
    }
});

function logout() {
    currentUser = null;
    showLogin();
    document.getElementById('loginForm').reset();
    document.getElementById('topicsList').innerHTML = '';

    document.getElementById('paperDetails').innerHTML = '';
    document.getElementById('paperTitle').style.display = 'none';
}

async function loadTopics() {
    if (!currentUser) return;
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('paperDetails').innerHTML = '';
    document.getElementById('paperTitle').style.display = 'none';
    
    try {
        const response = await apiCall(`/topics/${currentUser}`);
        const topics = await response.json();
        const topicsList = document.getElementById('topicsList');
        
        if (response.ok) {
            if (topics.length === 0) {
                topicsList.innerHTML = '<div class="no-topics">No topics found. Add your first topic!</div>';
            } else {
                topicsList.innerHTML = topics.map(topic => `
                    <div class="topic-item">
                        <div class="topic-content" onclick="viewPapers('${topic.replace(/'/g, "\\'")}')">
                            ${topic}
                        </div>
                        <div class="topic-actions">
                            <button class="btn btn-danger" onclick="deleteTopic('${topic.replace(/'/g, "\\'")}')">Delete</button>
                        </div>
                    </div>
                `).join('');
            }
        } else {
            const error = await response.json();
            topicsList.innerHTML = `<div class="error">${error.detail || 'Failed to load topics'}</div>`;
        }
    } catch (error) {
        document.getElementById('topicsList').innerHTML = '<div class="error">Failed to load topics. Network error.</div>';
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

document.getElementById('addTopicForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const topic = document.getElementById('newTopic').value;
    try {
        const response = await apiCall('/topics', 'POST', { email: currentUser, topic });
        const result = await response.json();
        if (response.ok) {
            document.getElementById('addTopicSuccess').style.display = 'block';
            document.getElementById('addTopicSuccess').textContent = 'Topic added successfully!';
            document.getElementById('addTopicError').style.display = 'none';
            document.getElementById('addTopicForm').reset();
            setTimeout(() => {
                showDashboard();
                document.getElementById('addTopicSuccess').style.display = 'none';
            }, 1500);
        } else {
            document.getElementById('addTopicError').style.display = 'block';
            document.getElementById('addTopicError').textContent = result.detail || 'Failed to add topic';
            document.getElementById('addTopicSuccess').style.display = 'none';
        }
    } catch (error) {
        document.getElementById('addTopicError').style.display = 'block';
        document.getElementById('addTopicError').textContent = 'Network error. Please try again.';
    }
});

async function deleteTopic(topic) {
    if (!confirm('Are you sure you want to delete this topic?')) return;
    try {
        const response = await apiCall('/topics', 'DELETE', { email: currentUser, topic });
        if (response.ok) {
            loadTopics();
        } else {
            const error = await response.json();
            alert(`Failed to delete topic: ${error.detail}`);
        }
    } catch (error) {
        alert('Network error. Please try again.');
    }
}

async function viewPapers(topic) {
    const paperDetails = document.getElementById('paperDetails');
    const paperLoading = document.getElementById('paperLoading');
    const paperTitle = document.getElementById('paperTitle');
    
    paperTitle.innerText = `Related Papers for: ${topic}`;
    paperTitle.style.display = 'block';
    paperDetails.innerHTML = '';
    paperLoading.style.display = 'block';

    try {
        const response = await apiCall(`/papers/${encodeURIComponent(topic)}`);
        const papers = await response.json();
        
        if (response.ok) {
            if (papers.length === 0) {
                paperDetails.innerHTML = '<div class="no-topics">No papers found for this topic.</div>';
            } else {
                paperDetails.innerHTML = papers.map(paper => `
                    <div class="paper-card">
                        <h3>${paper.title_paper || 'No Title'}</h3>
                        <em>By: ${paper.paper_authors || 'Unknown Authors'}</em>
                        <hr>
                        <h4>Content Summary</h4>
                        <p>${paper.content || 'No content available.'}</p>
                        <h4>Novelty Analysis</h4>
                        <p>${paper.novelty || 'No novelty analysis available.'}</p>
                    </div>
                `).join('');
            }
        } else {
            paperDetails.innerHTML = `<div class="error">${papers.detail || 'Failed to load papers.'}</div>`;
        }
    } catch (error) {
        paperDetails.innerHTML = '<div class="error">Network error. Could not fetch paper data.</div>';
    } finally {
        paperLoading.style.display = 'none';
    }
}

showLogin();