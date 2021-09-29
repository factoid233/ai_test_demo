import React from 'react';
import {
  Layout,
  Tabs,
} from "antd";
import '../App.css';
import AllTask from "./all_tasks";
import ActiveTasks from "./active_tasks";
import RunTest from "./run_test"

const { Content,Header } = Layout;
const { TabPane } = Tabs;



class TabChoose extends React.Component{
  constructor(props) {
    super(props);
    this.state = {isTick:true, activeKey:1};
    this.handleOnChange = this.handleOnChange.bind(this);
  }
  handleOnChange(e){
    let isTick = e === '1';
    this.setState({isTick:isTick,activeKey:e})
  }
  render() {
    return (
        <Tabs type="line" onChange={this.handleOnChange}>
          <TabPane tab="正在运行的测试" key={1} >
            <ActiveTasks isTick={this.state.isTick} />
          </TabPane>
          <TabPane tab="所有测试" key={2} >
            {this.state.activeKey === '2'?<AllTask />:null}
          </TabPane>
        </Tabs>
    );
  }
}


function AiTest() {
  return (
    <Layout>
      <Header style={{background:'#fff', height: "25%"}}>
        <RunTest/>
      </Header>
      <Content>
        <TabChoose/>
      </Content>

    </Layout>
  )
}

export default AiTest
