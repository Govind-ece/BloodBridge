<div align="center">

# 🩸 BloodBridge

### `A Python-Based Blood Donor Matching System`

**Connecting blood requests with potentially suitable donors through code.**

<br>

<img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/Project-Student%20Project-4F8CFF?style=for-the-badge">
<img src="https://img.shields.io/badge/Status-In%20Development-F39C12?style=for-the-badge">

</div>

---

## 🩸 About BloodBridge

**BloodBridge** is a Python-based blood donor matching system created as a
college programming project with a humanitarian purpose.

The idea is simple:

> **Organize donor information and help identify potentially suitable donors
> when a blood request is submitted.**

The project explores how programming, data management, and logical
decision-making can be applied to a real-world problem.

BloodBridge is an **educational prototype** and uses fictional or dummy
data for development and demonstration.

---

## 🎯 Project Objective

BloodBridge aims to demonstrate how a simple software system can organize
blood donor information and search for potentially suitable matches.

The project focuses on:

- 👤 Managing donor information
- 🩸 Handling blood requests
- 🧬 Checking blood-group compatibility
- ✅ Checking donor availability
- 📍 Considering location
- 💾 Managing stored data
- 🔎 Finding potentially suitable donors

---

## ✨ Features

### 👤 Donor Management

- Register donor information
- Store donor records
- Track donor availability
- Manage donor details

### 🩸 Blood Requests

- Create a blood request
- Specify required blood group
- Specify location
- Store request information

### 🧬 Blood Matching

- Compare requested and donor blood groups
- Apply predefined compatibility rules
- Identify potentially suitable donors

### 📍 Location Matching

- Consider donor/request location
- Filter potentially relevant donors based on location information

### 💾 Data Management

- Organize project data
- Store information locally
- Work with structured data
- Validate user input

---

## 🧠 How It Works

The basic idea behind BloodBridge is:

```text
              ┌───────────────────┐
              │   Blood Request   │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Blood Group Check │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Availability Check│
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Location Matching │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Potential Donors  │
              └───────────────────┘
