import React, { Component } from 'react';

import '../stylesheets/App.css';
import Question from './Question';
import Search from './Search';
import $ from 'jquery';
import { apiUrl } from './config';

class QuestionView extends Component {
  constructor(){
    super();
    this.state = {
      questions: [],
      page: 1,
      totalQuestions: 0,
      categories: {},
      currentCategory: null,
    }
  }

  componentDidMount() {
    this.categories = this.getCategories();
    this.getQuestions();
  }

  getCategories = () => {
    $.ajax({
      url: `${apiUrl}/api/v1/categories`,
      type: "GET",
      success: (result) => {
        const categories = {};
        result.forEach( cat => { categories[cat.id] = cat.type})
        this.setState({categories: categories})
        return;
      },
      error: (error) => {
          alert('Unable to load questions. Please try your request again')
          return;  
      }
    })
  }
  getQuestions = () => {
    $.ajax({
      url: `${apiUrl}/api/v1/questions?page=${this.state.page}`, //TODO: update request URL
      type: "GET",
      success: (result) => {
        this.setState( (prev) => {
          return { 
            questions: result,
            totalQuestions: result.length,
            currentCategory: (result[result.length - 1] !== undefined) ? 
              result[result.length - 1].category : prev.currentCategory 
          }
        })
        console.log(this.state.categories)
        return;
      },
      error: (error) => {
        alert('Unable to load questions. Please try your request again')
        return;
      }
    })
  }

  selectPage(num) {
    this.setState({page: num}, () => this.getQuestions());
  }

  createPagination(){
    let pageNumbers = [];
    let maxPage = Math.ceil(this.state.totalQuestions / 10)
    for (let i = 1; i <= maxPage; i++) {
      pageNumbers.push(
        <span
          key={i}
          className={`page-num ${i === this.state.page ? 'active' : ''}`}
          onClick={() => {this.selectPage(i)}}>{i}
        </span>)
    }
    return pageNumbers;
  }

  getByCategory= (id) => {
    $.ajax({
      url: `${apiUrl}/api/v1/categories/${id}/questions`, //TODO: update request URL
      type: "GET",
      success: (result) => {
        this.setState( (prev) => {
          return {  
            questions: result,
            totalQuestions: result.length,
            currentCategory: (result.length > 0) ? id : prev.currentCategory
          }
        })
        console.log(this.state)
        return;
      },
      error: (error) => {
        alert('Unable to load questions. Please try your request again')
        return;
      }
    })
  }

  submitSearch = (searchTerm) => {
    $.ajax({
      url: `${apiUrl}/api/v1/questions/search-term`, //TODO: update request URL
      type: "POST",
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({search_term: searchTerm}),
      xhrFields: {
        withCredentials: true
      },
      crossDomain: true,
      success: (result) => {
        this.setState( (prev) => {
          return {
            questions: result,
            totalQuestions: result.length,
            currentCategory: (result[0] !== undefined) ? result[0].category : prev.currentCategory 
          }
        })
        console.log(this.state);
        return;
      },
      error: (error) => {
        alert('Unable to load questions. Please try your request again')
        return;
      }
    })
  }

  questionAction = (id) => (action) => {
    if(action === 'DELETE') {
      if(window.confirm('are you sure you want to delete the question?')) {
        $.ajax({
          url: `${apiUrl}/api/v1/questions/${id}`, //TODO: update request URL
          type: "DELETE",
          success: (result) => {
            this.getQuestions();
          },
          error: (error) => {
            alert('Unable to load questions. Please try your request again')
            return;
          }
        })
      }
    }
  }

  render() {
    return (
      <div className="question-view">
        <div className="categories-list">
          <h2 onClick={() => {this.getQuestions()}}>Categories</h2>
          <ul>
            {Object.keys(this.state.categories).map((id, ) => (
              <li key={id} onClick={() => {this.getByCategory(id)}}>
                {this.state.categories[id]}
                <img className="category" src={`${this.state.categories[id].toLowerCase()}.svg`}/>
              </li>
            ))}
          </ul>
          <Search submitSearch={this.submitSearch}/>
        </div>
        <div className="questions-list">
          <h2>Questions</h2>
          {this.state.questions.map((q, ind) => (
            <Question
              key={q.id}
              question={q.question}
              answer={q.answer}
              category={this.state.categories[q.category]} 
              difficulty={q.difficulty}
              questionAction={this.questionAction(q.id)}
            />
          ))}
          <div className="pagination-menu">
            {this.createPagination()}
          </div>
        </div>

      </div>
    );
  }
}

export default QuestionView;
