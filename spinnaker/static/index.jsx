class SubmissionsList extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      submissions: [],
      expanded: null
    };
  }

  componentDidMount() {
		fetch("/v0/submissions")
    .then(response => response.json())
    .then(json => {
      this.setState(json);
    });  
  }

	handleSubmissionClick(submission) {
    submission == this.state.expanded ? 
      this.setState({expanded: null}) : this.setState({expanded: submission});
  }

  handleDownloadReceipt(submission) {
    if (submission.receipt) {
      let receipt = "data:text/tab-separated-values," 
        + encodeURIComponent(submission.receipt);
      window.open(receipt);
    }
  }

  render() {
    return (
      <cgl-data-table-container>
				<cgl-data-table>
					<cgl-data-table-row>
						<cgl-data-table-cell>Created</cgl-data-table-cell>
						<cgl-data-table-cell>ID</cgl-data-table-cell>
						<cgl-data-table-cell>Status</cgl-data-table-cell>
						<cgl-data-table-cell>Files</cgl-data-table-cell>
					</cgl-data-table-row>
					{this.state.submissions.map(submission => [
					<cgl-data-table-row onClick={this.handleSubmissionClick.bind(this, submission)}>
						<cgl-data-table-cell>{submission.created}</cgl-data-table-cell>
						<cgl-data-table-cell>{submission.id}</cgl-data-table-cell>
						<cgl-data-table-cell>{submission.status}</cgl-data-table-cell>
            <cgl-data-table-cell>
              <a href="#" onClick={this.handleDownloadReceipt.bind(this, submission)}>
                {submission.receipt && submission.receipt.split('\n').length - 2}
              </a>
            </cgl-data-table-cell>
					</cgl-data-table-row>,
          <div>
            {submission.receipt && submission.status == "invalid" && this.state.expanded == submission ?
              <cgl-data-table-row onClick={this.handleDownloadReceipt.bind(this, submission)}>
                <cgl-data-table-cell>
                  <div>{submission.validation_details}</div>
                </cgl-data-table-cell>
              </cgl-data-table-row>
              : <noscript />
            }
          </div>
          ])}
				</cgl-data-table>
      </cgl-data-table-container>
    );
  }
}

ReactDOM.render(<SubmissionsList/>, document.getElementById("submissions-list"));
