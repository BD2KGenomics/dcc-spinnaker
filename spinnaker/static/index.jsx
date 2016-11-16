function ErrorMessage(props) {
  let spaceAndWhat = "";
  if (props.what) {
    spaceAndWhat = " " + props.what;
  }

  return (
    <div className="ui negative icon message">
      <i className="bug icon"></i>
      <div className="content">
        <div className="header">
          Uh oh...
        </div>
        <p>
          Something went wrong{spaceAndWhat}. Please try again.
        </p>
      </div>
    </div>
  );
}

class ListSubmissions extends React.Component {
  render() {
    if (this.props.loadingStatus === "done") {
      if (this.props.submissions.length === 0) {
        return (
          <div className="ui huge message">
            <div className="header">
              No submissions
            </div>
            <p>
              You don't have any submissions... yet!
            </p>

            <p>
              You can add submissions with the command line interface thingy.
              Yeah. Cool.
            </p>
          </div>
        )
      } else {
        return (
          <table className="ui celled table">
            <thead>
              <tr>
                <th>Header</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Yo</td>
              </tr>
            </tbody>
          </table>
        )
      }
    } else if (this.props.loadingStatus === "loading") {
      return (
        <div className="ui icon message">
          <i className="notched circle loading icon"></i>
          <div className="content">
            <div className="header">
              One moment please...
            </div>
            <p>
              We're fetching that data for you.
            </p>
          </div>
        </div>
      )
    }

    return (
      <ErrorMessage what="fetching submissions from the server"/>
    )
  }
}

class ListSubmissionsPage extends React.Component {
  constructor() {
    super();

    this.state = {
      // can be: "loading", "error", or "ready"
      loadingStatus: "loading",
    };

    $.getJSON("/v0/submissions")
      .done((newState) => {
        _.extend(newState, {
          loadingStatus: "ready"
        });

        this.setState(newState);
      })
      .fail(() => {
        this.setState({
          loadingStatus: "error"
        });
      });
  }

  render() {
    let hello = "sdfsdf";

    return (
      <div className="ui container">
        <h1>Spinnaker submissions</h1>

        <ListSubmissions />
      </div>
    )
  }
}

ReactDOM.render(<ListSubmissionsPage />, document.getElementById("react-root"));
