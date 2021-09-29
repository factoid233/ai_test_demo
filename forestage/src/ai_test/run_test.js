import React, {useState} from "react";
import {
    Button,
    Cascader,
    notification,
    InputNumber,
    Form,
    Select,
    Row,
    Col
} from "antd";
import axios from "axios";

const {Option} = Select;

const layout = {
    labelCol: {
        // span: 2,
        // push: 5
    },
    wrapperCol: {
        // span: 2,
        // offset:10
        // push: 5
    },
    // layout: "inline",
};

class RunTest extends React.Component {
    formRef = React.createRef();

    constructor(props) {
        super(props);
        this.state = {
            choose: null,
            test_info: null,
            email_receivers: []
        };
    }


    componentDidMount() {
        this.request_data_envs();
    }

    request_data_envs() {
        let uri = "/celery/get_all_envs";
        axios.get(uri).then((response) => {
            this.setState({
                test_info: response.data.data.test_info,
                email_receivers: response.data.data.email_receivers,
            });
        });

    }

    set_value = (key, value) => {
        this.setState({[key]: value});
    };
    run_test = (data) => {
        let [testfunc, env_alias] = data['test_info']
        data['email_receivers'] = data['email_receivers'].join(",")
        let uri = "/api/" + testfunc
        let kwargs = {
            env_alias: env_alias,
        }
        delete data['test_info']
        let _params = Object.assign(kwargs, data)
        // axios会自动过滤调undefined的key
        axios.get(uri, {params: _params}).then((response) => {
            let type = null;
            if (response.data.code === 2000) {
                type = "success";
            } else {
                type = "error";
            }
            this.openNotificationWithIcon(
                type,
                response.data.code,
                response.data.msg
            );
        });
    };

    openNotificationWithIcon(type, msg, detail) {
        //右上角通知
        notification[type]({
            message: msg,
            description: detail,
        });
    }

    onFinish = (values) => {
        console.log(values);
        this.run_test(values)
    };

    generate_select_option() {
        let children = []
        let email_receivers = this.state.email_receivers
        for (const email of email_receivers) {
            children.push(<Option key={email}>{email}</Option>)
        }
        return children
    }

    render() {
        return (
            <Form
                {...layout}
                ref={this.formRef}
                name="control-ref"
                onFinish={this.onFinish}
                align="bottom"
                style={{paddingTop: "1%"}}
            >
                <Row>
                    <Col span={6}>
                        <Form.Item
                            label="选择测试类型"
                            name="test_info"
                            wrapperCol={{span: 20}}
                            labelCol={{}}
                            rules={[{required: true, message: '请选择'}]}
                        >
                            <Cascader
                                options={this.state.test_info}
                                // onChange={this.onChange}
                                expandTrigger="hover"
                                style={{width: "95%"}}
                                placeholder="请选择想要的测试类型"
                            />
                        </Form.Item>
                    </Col>
                    <Col span={10}>
                        <Form.Item
                            label="邮件接收者"
                            name="email_receivers"
                            wrapperCol={{span: 20}}
                            rules={[{required: true, message: '请选择'}]}
                        >
                            <Select
                                placeholder="Please choose"
                                // onChange={onGenderChange}
                                mode="multiple"
                                allowClear
                            >
                                {this.generate_select_option()}
                            </Select>
                        </Form.Item>
                    </Col>
                </Row>
                <Row gutter={13}>
                    <Col>
                        <Form.Item
                            label="并发数"
                            name="sema_num_request"
                        >
                            <InputNumber placeholder="数字"/>
                        </Form.Item>
                    </Col>
                    <Col>
                        <Form.Item
                            label="limit"
                            name="limit"
                            rules={[{message: ''}]}

                        >
                            <InputNumber placeholder="数字"/>
                        </Form.Item>
                    </Col>
                    <Col>
                        <Form.Item
                            label="limit_each"
                            name="limit_each"
                        >
                            <InputNumber placeholder="数字"/>
                        </Form.Item>
                    </Col>
                    <Col>
                        <Form.Item
                            label="困难程度"
                            name="level"
                        >
                            <Select
                                placeholder="Select level"
                                allowClear
                            >
                                <Option value={0}>困难</Option>
                                <Option value={1}>简单</Option>
                            </Select>
                        </Form.Item>
                    </Col>
                    <Col>
                        <Form.Item
                            label="超时时间(s)"
                            name="timeout"
                        >
                            <InputNumber placeholder="数字"/>
                        </Form.Item>
                    </Col>
                    <Col>
                        <Form.Item wrapperCol={{offset: 8, span: 16, push: 6}}>
                            <Button type="primary" htmlType="submit">
                                触发测试
                            </Button>
                        </Form.Item>
                    </Col>
                </Row>
            </Form>
        );
    }
}

export default RunTest;
