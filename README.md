# 💰 Personal Expense Tracker

A full-stack Python web application that helps users track, manage, and analyze their personal income and expenses.

## 🎯 Project Aim

To empower users to take control of their finances through a simple, secure, and visual platform for tracking income and expenses.

## ✨ Features

- User registration and login
- Secure password hashing
- Add, view, edit, and delete transactions
- Track income and expenses
- Categorize financial transactions
- Monthly income and expense summaries
- Interactive charts using Chart.js
- Six-month financial comparison
- Responsive design for desktop and mobile
- User-specific transaction management

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| Flask-SQLAlchemy | Database management |
| SQLite | Database |
| Flask-Login | User authentication |
| HTML5 | Page structure |
| CSS3 | Styling |
| Bootstrap 5 | Responsive UI |
| JavaScript | Frontend functionality |
| Chart.js | Financial visualizations |
| Git & GitHub | Version control |

## 📂 Project Structure

```text
personal-expense-tracker/
│
├── app.py
├── models.py
├── extensions.py
├── requirements.txt
├── .gitignore
├── templates/
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── add_expense.html
│   └── edit_expense.html
│
├── static/
└── instance/
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/fayisamian/personal-expense-tracker.git
```

### 2. Navigate into the project

```bash
cd personal-expense-tracker
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-own-secret-key
```

Use a strong, private secret key. Never upload your `.env` file.

### 7. Run the application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## 📊 Analytics

The application provides:

- Income and expense summaries
- Monthly financial overview
- Category-wise expense distribution
- Six-month income and expense comparison

## 🔒 Security

- Passwords are stored using password hashing.
- Login-protected pages restrict unauthorized access.
- Transactions are associated with individual users.
- Backend validation checks transaction data.
- Secret configuration and local database files are excluded from Git.

## 🚀 Project Status

- [x] Flask application development
- [x] User authentication
- [x] Transaction CRUD operations
- [x] Financial dashboard
- [x] Analytics and charts
- [x] Responsive UI
- [x] GitHub repository setup
- [ ] Live deployment

## 👨‍💻 Developer

**Mohammed Fayiz**

GitHub: [@fayisamian](https://github.com/fayisamian)

## 📄 License

License not yet selected.