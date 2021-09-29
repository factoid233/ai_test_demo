import React from "react";
import {Button, Progress, Space, Table} from "antd";
import jp from "jsonpath";
import axios from "axios";
import assert from "assert";
import {formatDateTime} from "../common";

class ActiveTasks extends React.Component {
  constructor(props) {
    super(props);
    this.state = { data: "",process_bar: null };
    this.process_bar = {}
    this.get_active_jobs = this.get_active_jobs.bind(this);
    this.stop_task = this.stop_task.bind(this);
    this.columns = [
      {
        title: "test_id",
        dataIndex: "test_id",
        key: "test_id",
        ellipsis: true
        // render: (text) => <a>{text}</a>,
      },
      {
        title: "测试类型",
        dataIndex: "type",
        key: "type",
      },
      {
        title: "测试环境",
        dataIndex: "env_type",
        key: "env_type",
      },
      {
        title: "状态",
        dataIndex: "status",
        key: "status",
        render: (text,record) => (
            <Progress percent={text} strokeWidth={12} />
        )
      },
      {
        title: "启动人",
        key: "people",
        dataIndex: "people",
      },
      {
        title: "启动时间",
        key: "time",
        dataIndex: "time",
      },
      {
        title: "Action",
        key: "action",
        render: (text, record) => (
          <Space size="middle">
            <Button
              onClick={() => this.stop_task(record.test_id)}
              type="primary"
              danger
            >
              停止
            </Button>
          </Space>
        ),
      },
    ];

    // this.get_data();
  }
  componentDidMount() {
    this.get_active_jobs()
  }
  componentWillUnmount() {
    this.clearTick();
  }
  tick() {
    this.get_active_jobs();
  }
  stop_task(test_id) {
    let task = jp.query(this.state.data, `$[?(@.test_id=='${test_id}')]`);
    let task_id = task[0]['test_id']
    let url = "/celery/stop_job/" + task_id;
    axios({
      method: "get",
      url: url,
    }).then((response) => {
      let resp =response.data;
      assert.strictEqual(resp.code, 2000);
    });

    let data_temp = this.state.data.filter(item=>item.test_id !== test_id);
    this.setState({data:data_temp});
  }
  get_process_bar(test_id){
    let url = "/celery/get_process_bar/" + test_id
    axios({
      method:"get",
      url:url
    }).then((resp)=> {

      let process_bar = resp.data.data
      let process_bar_percent = process_bar * 100
      process_bar_percent = process_bar_percent.toFixed(2)
      this.process_bar[test_id] = process_bar_percent
    }
    )
  }
  reshape_env_type(kwargs){
    let test_case_args = kwargs.test_case_args
    if (test_case_args){
      let env_name = test_case_args.env_type
      let env_url = test_case_args.env
      return env_name + "\n"+"(" + env_url + ")"
    }else{
      return ""
    }
  }

  format_data(response) {
    let data = response.data.data;
    if (!data) {
      return {};
    }
    let data2 = [];
    data.forEach((elem,index,array)=>{
      console.log(elem)
      let obj = {};
      let test_id = elem.id;
      obj["key"] = index;
      obj["test_id"] = test_id
      obj["type"] = elem.kwargs.testfunc;
      obj["env_type"] = elem.kwargs.env_alias;
      this.get_process_bar(test_id)
      obj["status"] = this.process_bar[test_id]
      obj["people"] = elem.kwargs.email_receivers;
      // 处理时间戳
      let time_start = new Date(elem.time_start * 1000);
      time_start = formatDateTime(time_start);
      obj["time"] = time_start;
      data2.push(obj);
      delete this.process_bar[test_id]
    })
    return data2
  }
  get_active_jobs() {
    const url = "/celery/active_jobs";
    axios({
      method: "get",
      url: url,
    }).then((response) => {
      let data = this.format_data(response);
      this.setState({ data: data });
    });
  }
  clearTick(){
    clearInterval(this.timeID);
    this.timeID = false;
  }
  setTick(){
    this.timeID = setInterval(() => this.tick(), 5000);
  }
  render() {
    if (!this.props.isTick){
      this.clearTick()
    }
    else if(!this.timeID ){
      this.setTick()
    }
    return <Table columns={this.columns} dataSource={this.state.data} />;
  }
}

export default ActiveTasks