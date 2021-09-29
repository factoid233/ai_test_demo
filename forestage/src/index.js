import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import { Layout, Menu, Breadcrumb } from "antd";
import {DashboardOutlined} from "@ant-design/icons";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
const {Content, Footer, Sider } = Layout;

class SiderDemo extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      collapsed: false,
    };
  }

  onCollapse = (collapsed) => {
    this.setState({ collapsed });
  };


  render() {
    const { collapsed } = this.state;
    return (
      <Router basename="/home">
        <Layout style={{ minHeight: "100vh" }}>
          <Sider
            collapsible
            collapsed={collapsed}
            onCollapse={this.onCollapse}
            theme="dark"
          >
            <Menu
              theme="dark"
              defaultSelectedKeys={["1"]}
              defaultOpenKeys={["1"]}
              mode="inline"
            >
              <Menu.Item key="1" icon={<DashboardOutlined />}>
                AI DashBoard
                <Link to="/ai" />
              </Menu.Item>
            </Menu>
          </Sider>
          <Layout className="site-layout">
            {/* <Header
              className="site-layout-background"
              style={{ padding: 0, background: "#fff" }}
            /> */}
            <Content style={{ margin: "0 16px" }}>
              <Breadcrumb style={{ margin: "16px 0" }}>
                <Breadcrumb.Item>AI DashBoard</Breadcrumb.Item>
                <Breadcrumb.Item>OCR</Breadcrumb.Item>
              </Breadcrumb>
              {/* <Route exact path="/uwsgi/ai" component={App} /> */}
              <Switch>
                <Route path="/ai" component={App} />
                <Route path="/" component={App} />
              </Switch>
            </Content>
            <Footer style={{ textAlign: "center" }}>
              Ant Design ©2018 Created by Ant UED
            </Footer>
          </Layout>
        </Layout>
      </Router>
    );
  }
}

ReactDOM.render(
  <SiderDemo/>,
  document.getElementById('root')
);

