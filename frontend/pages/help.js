import { Modal, Pressable, ScrollView, Text, View } from "react-native";
import styles from "../styles";
import { useTheme } from "@react-navigation/native";
import HelpText from "./helpText";
import Button from "../components/button";


/*
props:

    - visible
    - onClose
*/

export default function Help(props) {

    const colors = useTheme().colors;

    return (

        <Modal
            transparent={true}
            visible={props.visible}
            animationType={"fade"}
        >
            <View style={{

                flex: 1,
                backgroundColor: 'rgba(0.5, 0.5, 0.5, 0.5)',
                padding: 16,
            }}>

                <View style={[{

                    flex: 1,
                    padding: 16,
                },
                    styles(colors).maxWidth,
                    styles(colors).modal,
                ]}>
                    {/* Header */}

                    <View style={[

                        {
                            paddingBottom: 8,
                            flexDirection: 'row',
                            width: '100%',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                        } 
                    ]}>
                        <Text style={[

                            styles(colors).text,
                            styles(colors).title
                        ]}>
                            Help

                        </Text>
                        
                        <Button

                            style={{

                                alignSelf: 'flex-end'
                            }}

                            onPress={props.onClose}
                        >
                            X

                        </Button>
                    </View>
                    
                    {/* Main Text */}
                    <View style={styles(colors).scrollViewContainer}>
                        <ScrollView>
                            <Text style={styles(colors).text}><HelpText/></Text>
                        </ScrollView>
                    </View>
                    
                    <View style={{

                        paddingTop: 8,
                        alignItems: 'center',
                    }}>
                        <Button 

                            onPress={props.onClose}
                            primary={true}
                        >
                            Done
                        </Button>
                    </View>
                </View>
            </View>
        </Modal>
    )
}

/*

                        <Pressable style={[

                            styles(colors).container,
                        {
                            alignSelf: 'flex-end'
                        }]}
                            onPress={props.onClose}
                        >
                            <Text style={styles(colors).text}>Close</Text>

                        </Pressable>
*/
