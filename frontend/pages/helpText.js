import { Text } from "react-native"

export default function HelpText(props) {

    return (

        <Text style={props.style}>
            
            <Text
            
                style={{

                    fontWeight: 'bold'
                }}
            >
                Welcome to the chatbot. Tell us your desired train journey and we will find you the best ticket possible!
            </Text>

            {'\n'}{'\n'}

            The chatbot will ask for any missing information so do not worry if you cannot think of everything right now!
            
            {'\n'}{'\n'}

            <Text

                style={{

                    fontWeight: 'bold'
                }}
            >
                If you want to undo your previous statement, simply type 'undo'.
                {'\n\n'}
                If you want to reset your ticket, simply type 'reset'.
            </Text>

            {'\n'}{'\n'}{'\n'}

            <Text
            
                style={{

                    fontWeight: 'bold'
                }}
            >
                The chatbot will ask for the following information:
            </Text>

            {'\n'}{'\n'} - The departure time for your journey.
            {'\n'}{'\n'} - Your station of arrival. If you do not know the exact station's name, type the name of the city or town and we will tell you all the possibilities
            {'\n'}{'\n'} - Your station of departure.
            {'\n'}{'\n'} - If you are getting a return ticket and the time and date of departure from the return station.

            <Text

                style={{

                    fontWeight: 'bold'
                }}
            >
                Do not talk about the time and date of your return in your first message, the chatbot will ask for this after. 
            </Text>

            {'\n'}{'\n'}{'\n'}

            <Text
            
                style={{

                    fontWeight: 'bold'
                }}
            >
                This chatbot was made by the following people:
            </Text>

            {'\n'} - Liam Farese
            {'\n'} - Riley Braybrook
            {'\n'} - Hector Selby Reimundez

            
            {'\n'}{'\n'}
            
            We hope you find this chatbot useful and good luck on your journey!

        </Text>
    )
}
