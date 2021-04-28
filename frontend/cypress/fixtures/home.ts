interface apiCall {
    method: "GET" | "POST" | "DELETE";
    url: string;   
}

const searchQuestions: apiCall = {
    method: "POST",
    url: "http://localhost:5000/api/v1/questions/search-term"
} 

const deleteQuestions: apiCall = {
    method: "DELETE",
    url: "http://localhost:5000/api/v1/questions/**"
}

const apiIntegration = {
    search: searchQuestions,
    delete: deleteQuestions
}

const categories: string[] = [
    "Science", 
    "Art",
    "History",,
    "Entertainment",
    "Sports"
]

export { categories, apiIntegration }