-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3307
-- Generation Time: Feb 26, 2019 at 01:35 PM
-- Server version: 10.1.36-MariaDB
-- PHP Version: 5.6.38

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `forum_structures`
--

-- --------------------------------------------------------

--
-- Table structure for table `FORUM_FIELDS`
--

CREATE TABLE `FORUM_FIELDS` (
  `website_id` int(11) NOT NULL,
  `thread_pool_xpath` varchar(300) NOT NULL,
  `thread_pool_class` varchar(300) NOT NULL,
  `subforum_next_page_xpath` varchar(300) NOT NULL,
  `subforum_next_page_class` varchar(300) NOT NULL,
  `thread_post_count_xpath` varchar(300) NOT NULL,
  `thread_post_count_class` varchar(300) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Table structure for table `LOGIN_FIELDS`
--

CREATE TABLE `LOGIN_FIELDS` (
  `website_id` int(11) NOT NULL,
  `signin_xpath` varchar(300) NOT NULL,
  `username_xpath` varchar(300) NOT NULL,
  `password_xpath` varchar(300) NOT NULL,
  `login_xpath` varchar(300) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Table structure for table `POST_DUMPS`
--

CREATE TABLE `POST_DUMPS` (
  `hash` varchar(300) NOT NULL,
  `website_id` int(11) NOT NULL,
  `thread_url` varchar(300) NOT NULL,
  `thread_name` varchar(500) NOT NULL,
  `author` varchar(300) NOT NULL,
  `date` varchar(300) NOT NULL,
  `post_count` varchar(300) NOT NULL,
  `post_content` mediumtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `THREAD_FIELDS`
--

CREATE TABLE `THREAD_FIELDS` (
  `website_id` int(11) NOT NULL,
  `post_pool_class` varchar(300) NOT NULL,
  `post_pool_xpath` varchar(300) NOT NULL,
  `date_class` varchar(300) NOT NULL,
  `date_xpath` varchar(300) NOT NULL,
  `author_class` varchar(300) NOT NULL,
  `author_xpath` varchar(300) NOT NULL,
  `post_count_class` varchar(300) NOT NULL,
  `post_count_xpath` varchar(300) NOT NULL,
  `post_text_class` varchar(300) NOT NULL,
  `post_text_xpath` varchar(300) NOT NULL,
  `thread_next_page_class` varchar(300) NOT NULL,
  `thread_next_page_xpath` varchar(300) NOT NULL,
  `thread_title_class` varchar(300) NOT NULL,
  `thread_title_xpath` varchar(300) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `THREAD_LIST`
--

CREATE TABLE `THREAD_LIST` (
  `thread_url` varchar(300) NOT NULL,
  `post_count` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `WEBSITE`
--

CREATE TABLE `WEBSITE` (
  `website_id` int(11) NOT NULL,
  `url` varchar(300) NOT NULL,
  `forum_xpaths` varchar(300) NOT NULL,
  `subforum_xpaths` varchar(300) DEFAULT NULL,
  `is_vbullettin` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


--
-- Indexes for dumped tables
--

--
-- Indexes for table `FORUM_FIELDS`
--
ALTER TABLE `FORUM_FIELDS`
  ADD PRIMARY KEY (`website_id`),
  ADD UNIQUE KEY `website_id` (`website_id`);

--
-- Indexes for table `LOGIN_FIELDS`
--
ALTER TABLE `LOGIN_FIELDS`
  ADD PRIMARY KEY (`website_id`),
  ADD UNIQUE KEY `website_id` (`website_id`);

--
-- Indexes for table `THREAD_FIELDS`
--
ALTER TABLE `THREAD_FIELDS`
  ADD PRIMARY KEY (`website_id`),
  ADD UNIQUE KEY `website_id` (`website_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `FORUM_FIELDS`
--
ALTER TABLE `FORUM_FIELDS`
  MODIFY `website_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `LOGIN_FIELDS`
--
ALTER TABLE `LOGIN_FIELDS`
  MODIFY `website_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `THREAD_FIELDS`
--
ALTER TABLE `THREAD_FIELDS`
  MODIFY `website_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
