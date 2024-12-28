# Twitter Trend Extractor

Twitter Trend Extractor is a Flask-based API that scrapes top five trending topics from Twitter using Selenium and stores the extracted data in a MongoDB database. It is designed to handle dynamic web interactions while ensuring smooth proxy using ProxyMesh and authentication integration.  

## Technologies and Libraries  

The project utilizes the following technologies and libraries:

- **Python**: Main programming language
- **Flask**: Web framework to expose the scraping functionality as an API
- **Selenium WebDriver**: For automated browser interactions
- **Selenium Wire**: To handle proxy settings
- **MongoDB**: NoSQL database for storing extracted trends
- **dotenv**: For managing environment variables
- **Flask-CORS**: To enable cross-origin resource sharing

## Installation and Setup  

### Prerequisites  
1. **Python 3.8+** must be installed on your system.  
2. **MongoDB** should be installed locally or a cloud database connection (e.g., MongoDB Atlas).  
3. Install **Google Chrome** (ensure version compatibility with ChromeDriver).  
4. Install **ChromeDriver** and set the path in your `.env` file.  
5. A valid **Twitter account** is required to log in.
6. A valid **ProxyMesh account** is required for proxy. 

### 1. Clone the Repository  
```bash
git clone https://github.com/yourusername/twitter-trend-extractor.git
cd twitter-trend-extractor
```

### 2. Install Dependencies
Install the required libraries using the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root and configure the following environment variables:

```bash
# MongoDB  
MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/twitter_trends?retryWrites=true&w=majority  

# Twitter Credentials  
TWITTER_USERNAME=your_twitter_username  
TWITTER_PASSWORD=your_twitter_password  
TWITTER_HANDLE=your_twitter_handle  # Only if required during additional verification  

# Proxy  
PROXY_USER=your_proxymesh_username  
PROXY_PASSWORD=your_proxymesh_password  

# ChromeDriver Path  
CHROMEDRIVER_PATH=/path/to/your/chromedriver  
```

### 4. Running the Flask API
Start the Flask API by running the following command:

```bash
python app.py
```
The API will run at `http://127.0.0.1:5000/` by default.

#### Available Endpoints:
**GET** `/scrape-trends`: Scrapes Twitter for trending topics and stores them in MongoDB.

### 5. Using the Web Interface
After starting the Flask API, open the index.html file in your browser. This file fetches the trends from the API and displays them in a user-friendly format.

## Connect with Me

Feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/aslam8483).
